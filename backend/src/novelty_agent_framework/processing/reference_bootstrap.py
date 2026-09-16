"""Deterministic citation resolution and subject-reference materialization."""

from __future__ import annotations

import asyncio
import hashlib
import math
import re
from collections import Counter
from collections.abc import Sequence
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Iterable

from ..persistence import SubjectReferenceStore
from ..ports import SearchHit
from ..schemas import (
    Artifact,
    ArtifactRole,
    ContentExtent,
    ExternalIdentifier,
    ParsedCitation,
    ReferenceBootstrapEntry,
    ReferenceBootstrapManifest,
    ReferenceManifest,
    ReferenceResolveAttempt,
    ResolutionStatus,
)
from ..tools.database_search.structured_retrieval import (
    StructuredRetrievalAdapter,
    _invoke_provider,
)


class CitationParser:
    DOI = re.compile(r"(?i)\b(?:doi\s*:\s*|https?://doi\.org/)?(10\.\d{4,9}/[-._;()/:A-Z0-9]+)")
    ARXIV = re.compile(r"(?i)(?:arxiv\s*:\s*|arxiv\.org/(?:abs|pdf)/)([a-z.-]+/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?")
    URL = re.compile(r"https?://[^\s<>\]\[\"']+")
    YEAR = re.compile(r"(?<!\d)((?:18|19|20)\d{2})(?!\d)")
    # GB/T 7714 的文献类型标识：题名以它结尾，其后才是刊名/会议名等出处。
    # 长代码排在前面，避免 [J/OL] 被 [J] 提前匹配。
    TYPE_MARKER = re.compile(
        r"\[\s*(?:EB/OL|DB/OL|CP/DK|J/OL|C/OL|M/OL|D/OL|DB|CP|EB|J|C|M|D|R|S|N|P|G|Z)\s*\]",
        re.IGNORECASE,
    )
    # 序号标记（[1] / [12]）不是文献类型。
    ORDINAL_MARKER = re.compile(r"^\s*\[\d{1,4}\]\s*")

    def parse(self, raw: str) -> ParsedCitation:
        text = " ".join(raw.split())
        doi_match = self.DOI.search(text)
        arxiv_match = self.ARXIV.search(text)
        url_match = self.URL.search(text)
        year_match = self._find_year(text)
        doi = doi_match.group(1).rstrip(".,;)") if doi_match else None
        url = url_match.group(0).rstrip(".,;)") if url_match else None
        # A deliberately conservative title heuristic: quoted text first, then
        # the longest sentence-like segment after removing identifiers.
        quoted = re.search(r"[\"“](.{4,}?)[\"”]", text)
        segments = [part.strip(" .;,，。") for part in re.split(r"[。;]", text)]
        candidates = [part for part in segments if len(part) >= 8 and not self.URL.fullmatch(part)]
        title = quoted.group(1).strip() if quoted else (max(candidates, key=len) if candidates else None)
        if title == text and not (year_match or doi_match or arxiv_match or url_match):
            title = None
        authors: list[str] = []
        if title:
            prefix = text.split(title, 1)[0].strip(" []().,;，。").replace(" et al", "")
            if prefix and len(prefix) < 160:
                authors = [item.strip() for item in re.split(r",|，|\band\b|和", prefix) if item.strip()]
        authors, title = self._split_gbt7714(text, title, authors)
        if title:
            warnings = []
        else:
            warnings = ["citation could not be structurally parsed"]
        return ParsedCitation(
            title=title,
            authors=authors,
            year=int(year_match.group(1)) if year_match else None,
            doi=doi.lower() if doi else None,
            url=url,
            arxiv_id=arxiv_match.group(1) if arxiv_match else None,
            warnings=warnings,
        )

    def _split_gbt7714(
        self, text: str, title: str | None, authors: list[str]
    ) -> tuple[list[str], str | None]:
        """按文献类型标识切出作者段与题名段。

        GB/T 7714 形如 ``[1] 作者 A, 作者 B. 题名[J]. 刊名, 年, 卷(期): 页码.``；
        没有类型标识时保留原启发式结果，避免改变既有行为。
        """

        marker = self.TYPE_MARKER.search(text)
        if marker is None:
            return authors, title
        head = self.ORDINAL_MARKER.sub("", text[: marker.start()], count=1)
        author_part, separator, title_part = head.partition(". ")
        title_text = (title_part if separator else head).strip(" .;,，。")
        if not title_text:
            return authors, title
        parsed_authors: list[str] = []
        if separator:
            cleaned = author_part.strip(" []().,;，。").replace(" et al", "")
            if cleaned and len(cleaned) < 160:
                parsed_authors = [
                    item.strip(" .")
                    for item in re.split(r",|，|;|；|\band\b|和", cleaned)
                    if item.strip(" .")
                ]
        return (parsed_authors or authors), title_text

    def _find_year(self, text: str) -> re.Match[str] | None:
        """定位出版年，避免把标识符里的数字当成年份。

        arXiv ID 形如 ``1907.04931``，直接全局匹配年份会把 1907 误判为出版年
        （实测 ``[7] ... arXiv preprint arXiv:1907.04931, 2019.`` 被判成 1907）。
        所以先屏蔽 DOI/arXiv/URL 片段，再优先在文献类型标识之后（即出处区）找年份。
        """

        marker = self.TYPE_MARKER.search(text)
        if marker is not None:
            found = self.YEAR.search(self._mask_identifiers(text[marker.end() :]))
            if found is not None:
                return found
        return self.YEAR.search(self._mask_identifiers(text))

    def _mask_identifiers(self, text: str) -> str:
        """把 DOI/arXiv/URL 替换为等长空白，保留其余文本的偏移语义。"""

        masked = text
        for pattern in (self.DOI, self.ARXIV, self.URL):
            masked = pattern.sub(lambda match: " " * len(match.group(0)), masked)
        return masked


@dataclass(frozen=True)
class CitationMatch:
    status: ResolutionStatus
    selected: SearchHit | None = None
    candidates: tuple[SearchHit, ...] = ()


class CitationMatcher:
    """One conservative identity policy shared by every provider."""

    def match(self, citation: ParsedCitation, hits: Iterable[SearchHit]) -> CitationMatch:
        unique = list({_hit_key(hit): hit for hit in hits}.values())
        if citation.doi:
            exact = [h for h in unique if h.doi and _doi(h.doi) == _doi(citation.doi)]
            if len(exact) == 1:
                return CitationMatch(ResolutionStatus.RESOLVED, exact[0], tuple(exact))
            if len(exact) > 1:
                return CitationMatch(ResolutionStatus.AMBIGUOUS, candidates=tuple(exact))
        if citation.arxiv_id:
            exact = [h for h in unique if _arxiv(h.document_id) == _arxiv(citation.arxiv_id) or _arxiv(h.external_id or "") == _arxiv(citation.arxiv_id)]
            if len(exact) == 1:
                return CitationMatch(ResolutionStatus.RESOLVED, exact[0], tuple(exact))
        if not citation.title:
            return CitationMatch(ResolutionStatus.NOT_FOUND, candidates=tuple(unique))
        scored = sorted(((self._score(citation, h), h) for h in unique), key=lambda x: x[0], reverse=True)
        plausible = [(score, hit) for score, hit in scored if score >= 0.82]
        if not plausible:
            return CitationMatch(ResolutionStatus.NOT_FOUND, candidates=tuple(unique))
        if len(plausible) > 1 and plausible[0][0] - plausible[1][0] < 0.06:
            return CitationMatch(ResolutionStatus.AMBIGUOUS, candidates=tuple(h for _, h in plausible))
        return CitationMatch(ResolutionStatus.RESOLVED, plausible[0][1], tuple(h for _, h in plausible))

    @staticmethod
    def _score(citation: ParsedCitation, hit: SearchHit) -> float:
        title_score = SequenceMatcher(None, _text(citation.title or ""), _text(hit.title)).ratio()
        if title_score == 1.0:
            return 1.0
        authors = {_text(a) for a in citation.authors if _text(a)}
        candidate_authors = {_text(a) for a in hit.authors if _text(a)}
        author_score = len(authors & candidate_authors) / len(authors) if authors else 0.5
        year_score = 0.5 if citation.year is None or hit.year is None else float(citation.year == hit.year)
        return 0.75 * title_score + 0.15 * author_score + 0.10 * year_score


@dataclass(frozen=True)
class ReferenceTarget:
    """一个待检索目标（通常是查新点），用于挑选值得联网解析的参考文献。"""

    target_id: str
    text: str


def _tokens(value: str) -> list[str]:
    """与 ReferenceSearchTool 一致的词元切分（拉丁词 + 单个中文字）。"""

    normalized = unicodedata.normalize("NFKC", value).casefold()
    latin = re.findall(r"[a-z0-9]+", normalized)
    chinese = re.findall(r"[\u4e00-\u9fff]", normalized)
    return latin + chinese


def _reference_text(parsed: ParsedCitation, raw: str) -> str:
    """参考文献的可比文本：题名为主，作者与年份补充。"""

    parts = [parsed.title or raw, " ".join(parsed.authors)]
    if parsed.year is not None:
        parts.append(str(parsed.year))
    return " ".join(part for part in parts if part)


def select_reference_ordinals(
    references: Sequence[str],
    targets: Sequence[ReferenceTarget],
    *,
    per_target_limit: int,
    parser: CitationParser | None = None,
    min_score: float = 0.0,
    include_direct_identifiers: bool = False,
) -> list[int]:
    """按词面相关性为每个目标挑选 top-K 参考文献，返回并集（升序）。

    纯本地计算，不触网。未选中不代表“查不到”，只是本轮不为此发起检索；
    这样 90 条参考文献不会全部变成 90 次 arXiv 请求。
    目标为空或 ``per_target_limit <= 0`` 时退化为“全选”，保持原有行为。
    """

    if not targets or per_target_limit <= 0:
        return list(range(1, len(references) + 1))
    resolved_parser = parser or CitationParser()
    parsed = [resolved_parser.parse(raw) for raw in references]
    documents = [Counter(_tokens(_reference_text(item, raw))) for item, raw in zip(parsed, references)]
    document_frequency: Counter[str] = Counter()
    for terms in documents:
        document_frequency.update(terms.keys())
    total = len(documents)
    selected: set[int] = set()
    for target in targets:
        query = Counter(_tokens(target.text))
        if not query:
            continue
        scored: list[tuple[float, int]] = []
        for ordinal, terms in enumerate(documents, start=1):
            score = 0.0
            for token, query_tf in query.items():
                document_tf = terms.get(token, 0)
                if not document_tf:
                    continue
                weight = math.log((total + 1) / (document_frequency[token] + 1)) + 1.0
                score += query_tf * document_tf * weight
            if score > min_score:
                scored.append((score, ordinal))
        scored.sort(key=lambda item: (-item[0], item[1]))
        for _score, ordinal in scored[:per_target_limit]:
            selected.add(ordinal)
    if include_direct_identifiers:
        for ordinal, item in enumerate(parsed, start=1):
            if item.arxiv_id or item.doi or item.url:
                selected.add(ordinal)
    return sorted(selected)


class ReferenceProviderRegistry:
    def __init__(self, providers: Iterable[Any] = ()) -> None:
        self._providers: dict[str, Any] = {}
        for provider in providers:
            self.register(provider)

    def register(self, provider: Any) -> None:
        provider_id = str(getattr(provider, "source_id", getattr(provider, "provider_id", ""))).strip().lower()
        if not provider_id:
            raise ValueError("provider requires source_id or provider_id")
        if provider_id in self._providers:
            raise ValueError(f"duplicate provider {provider_id!r}")
        self._providers[provider_id] = provider

    def providers(self, only: str | None = None) -> list[tuple[str, Any]]:
        if only is None:
            return list(self._providers.items())
        key = only.strip().lower()
        return [(key, self._providers[key])] if key in self._providers else []


class ReferenceBootstrapService:


    def __init__(self, registry: ReferenceProviderRegistry, store: SubjectReferenceStore | None = None, *, matcher: CitationMatcher | None = None, parser: CitationParser | None = None, max_concurrency: int = 4) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be positive")
        self.registry, self.store = registry, store or SubjectReferenceStore()
        self.matcher, self.parser = matcher or CitationMatcher(), parser or CitationParser()
        self.max_concurrency = max_concurrency
        self.adapter = StructuredRetrievalAdapter()

    async def bootstrap(
        self,
        paper_id: str,
        references: list[str],
        *,
        force: bool = False,
        retry_failed: bool = False,
        provider: str | None = None,
        dry_run: bool = False,
        targets: Sequence[ReferenceTarget] | None = None,
        per_target_limit: int = 0,
        include_direct_identifiers: bool = False,
    ) -> ReferenceBootstrapManifest:
        """解析参考文献；给定 ``targets`` 时只联网解析被选中的少数条目。

        未选中的条目记录为 ``SKIPPED``：它表示“本轮没有为它发起检索”，不是
        “查不到”。这样 90 条参考文献不会变成 90 次 arXiv 请求。

        ``include_direct_identifiers=True`` 时，**带显式 ``arxiv_id`` / ``doi`` /
        ``url`` 的条目一律纳入解析**，不受词面 top-K 限制。实测（MF2033k6lC，91 条
        参考文献）：能解析成功的条目与“带显式 ID”高度重合 —— 19 条带 ID 里 18 条
        成功，72 条无 ID 里 0 条成功。只走词面打分时那 19 条里通常只选中 1 条，
        于是选中的 10 条里 6 条注定 ``not_found``，reference_search 的本地语料被压到
        个位数。默认 False 以保持既有调用方行为不变。
        """
        ledger = self.store.load_bootstrap(paper_id)
        existing = {entry.reference_id: entry for entry in ledger.entries}
        semaphore = asyncio.Semaphore(self.max_concurrency)

        filtering = bool(targets) and per_target_limit > 0
        selected = set(
            select_reference_ordinals(
                references,
                targets or (),
                per_target_limit=per_target_limit,
                parser=self.parser,
                include_direct_identifiers=include_direct_identifiers,
            )
        )

        async def run(ordinal: int, raw: str) -> ReferenceBootstrapEntry:
            reference_id = self.adapter.stable_id("ref", paper_id, str(ordinal), raw)
            old = existing.get(reference_id)
            if filtering and ordinal not in selected:
                # 预筛未命中：保留已有结果，绝不为此发起网络请求。
                if old is not None:
                    return old
                return ReferenceBootstrapEntry(
                    reference_id=reference_id,
                    ordinal=ordinal,
                    raw_reference=raw,
                    parsed=self.parser.parse(raw),
                    resolution_status=ResolutionStatus.SKIPPED,
                    attempts=[],
                )
            if filtering:
                # 选中项只在“从未尝试过”（SKIPPED/缺失）、force 或 retry_failed
                # 时才联网；已解析过的条目跨运行复用，不重复烧请求。
                needs_attempt = old is None or (
                    old.resolution_status is ResolutionStatus.SKIPPED
                )
                if (
                    retry_failed
                    and old is not None
                    and old.resolution_status
                    in {ResolutionStatus.FAILED, ResolutionStatus.NOT_FOUND}
                ):
                    needs_attempt = True
                if not needs_attempt and not force:
                    return old
            elif old and not force and not (
                retry_failed
                and old.resolution_status
                in {ResolutionStatus.FAILED, ResolutionStatus.NOT_FOUND}
            ):
                return old
            async with semaphore:
                entry = await self._resolve_one(paper_id, reference_id, ordinal, raw, provider=provider, dry_run=dry_run)
                existing[reference_id] = entry
                current = ReferenceBootstrapManifest(
                    subject_paper_id=paper_id,
                    references_digest=references_digest(references),
                    entries=sorted(existing.values(), key=lambda x: x.ordinal),
                )
                self.store.persist_bootstrap(paper_id, current)
                return entry

        entries = await asyncio.gather(*(run(i, raw) for i, raw in enumerate(references, 1)))
        result = ReferenceBootstrapManifest(
            subject_paper_id=paper_id,
            references_digest=references_digest(references),
            entries=list(entries),
        )
        self.store.persist_bootstrap(paper_id, result)
        return result

    async def _resolve_one(self, paper_id: str, reference_id: str, ordinal: int, raw: str, *, provider: str | None, dry_run: bool) -> ReferenceBootstrapEntry:
        parsed = self.parser.parse(raw)
        attempts: list[ReferenceResolveAttempt] = []
        providers = self.registry.providers(provider)
        if dry_run:
            attempts.append(self._attempt(reference_id, "bootstrap", "dry_run", raw, "planned"))
            return ReferenceBootstrapEntry(reference_id=reference_id, ordinal=ordinal, raw_reference=raw, parsed=parsed, resolution_status=ResolutionStatus.NOT_FOUND, attempts=attempts)
        try:
            for namespace, value in (("doi", parsed.doi), ("arxiv", parsed.arxiv_id), ("url", parsed.url)):
                if not value:
                    continue
                for provider_id, capability in providers:
                    resolver = getattr(capability, "resolve_identifier", None)
                    if resolver is None:
                        continue
                    try:
                        hit = await _invoke_provider(
                            resolver,
                            ExternalIdentifier(namespace=namespace, value=value),
                        )
                    except Exception as exc:
                        attempts.append(self._attempt(reference_id, provider_id, f"{namespace}_exact", value, "failed", error=f"{type(exc).__name__}: {exc}"[:1000]))
                        continue
                    hits = [hit] if hit else []
                    match = self.matcher.match(parsed, hits)
                    attempts.append(self._attempt(reference_id, provider_id, f"{namespace}_exact", value, match.status.value, hits))
                    if match.status == ResolutionStatus.RESOLVED:
                        return self._materialize(reference_id, ordinal, raw, parsed, attempts, provider_id, match.selected, paper_id=paper_id)
            gathered: list[tuple[str, SearchHit]] = []
            for provider_id, capability in providers:
                search = getattr(capability, "search_known_item", None)
                if search is None:
                    continue
                try:
                    hits = list(await _invoke_provider(search, parsed, limit=5))
                except Exception as exc:
                    attempts.append(self._attempt(reference_id, provider_id, "known_item", parsed.title or raw, "failed", error=f"{type(exc).__name__}: {exc}"[:1000]))
                    continue
                gathered.extend((provider_id, hit) for hit in hits)
                attempts.append(self._attempt(reference_id, provider_id, "known_item", parsed.title or raw, "completed", hits))
            match = self.matcher.match(parsed, [hit for _, hit in gathered])
            if match.status == ResolutionStatus.RESOLVED and match.selected:
                selected_provider = next(pid for pid, hit in gathered if _hit_key(hit) == _hit_key(match.selected))
                return self._materialize(reference_id, ordinal, raw, parsed, attempts, selected_provider, match.selected, paper_id=paper_id)
            if not attempts:
                attempts.append(self._attempt(reference_id, "bootstrap", "unavailable", raw, "not_found"))
            status = ResolutionStatus.FAILED if attempts and all(item.status == "failed" for item in attempts) else match.status
            return ReferenceBootstrapEntry(reference_id=reference_id, ordinal=ordinal, raw_reference=raw, parsed=parsed, resolution_status=status, attempts=attempts)
        except Exception as exc:
            attempts.append(self._attempt(reference_id, "bootstrap", "resolution", raw, "failed", error=f"{type(exc).__name__}: {exc}"[:1000]))
            return ReferenceBootstrapEntry(reference_id=reference_id, ordinal=ordinal, raw_reference=raw, parsed=parsed, resolution_status=ResolutionStatus.FAILED, attempts=attempts)

    def _materialize(self, reference_id: str, ordinal: int, raw: str, parsed: ParsedCitation, attempts: list[ReferenceResolveAttempt], provider_id: str, hit: SearchHit | None, *, paper_id: str) -> ReferenceBootstrapEntry:
        assert hit is not None
        if not paper_id:
            raise ValueError("paper_id is required for materialization")
        work, record, _ = self.adapter.adapt_hit(hit, provider_id, datetime.now(timezone.utc))
        artifacts: list[Artifact] = []
        if hit.abstract.strip():
            artifact_id = self.adapter.stable_id("art", record.source_record_id, "abstract")
            self.store.write_document(paper_id, work_id=work.work_id, artifact_id=artifact_id, extension="txt", content=hit.abstract)
            artifacts.append(Artifact(artifact_id=artifact_id, work_id=work.work_id, source_record_id=record.source_record_id, role=ArtifactRole.ABSTRACT, media_type="text/plain", relative_path=f"documents/{work.work_id}/{artifact_id}.txt", sha256=hashlib.sha256(hit.abstract.encode()).hexdigest(), byte_size=len(hit.abstract.encode()), content_extent=ContentExtent.FULL, acquired_at=datetime.now(timezone.utc), provenance={"source": "search_hit.abstract"}))
        # 在锁内重新读取再合并：bootstrap 并发解析多条引文，各自持有旧副本整份
        # 写回会互相覆盖（条目静默消失，只剩悬空制品）。
        self.store.merge_manifest(paper_id, works=[work], source_records=[record], artifacts=artifacts)
        attempts[-1] = attempts[-1].model_copy(update={"selected_work_id": work.work_id})
        return ReferenceBootstrapEntry(reference_id=reference_id, ordinal=ordinal, raw_reference=raw, parsed=parsed, resolution_status=ResolutionStatus.RESOLVED, resolved_work_id=work.work_id, attempts=attempts)

    @staticmethod
    def _attempt(reference_id: str, provider_id: str, method: str, query: str, status: str, hits: list[SearchHit] | None = None, error: str | None = None) -> ReferenceResolveAttempt:
        return ReferenceResolveAttempt(attempt_id=StructuredRetrievalAdapter.stable_id("att", reference_id, provider_id, method, str(len(hits or []))), provider_id=provider_id, method=method, query_or_identifier=query, status=status, candidate_work_ids=[StructuredRetrievalAdapter.stable_id("candidate", _hit_key(h)) for h in hits or []], error=error)


def _text(value: str) -> str:
    return re.sub(r"[^\w]+", "", unicodedata.normalize("NFKC", value).casefold())


def references_digest(references: Iterable[str]) -> str:
    """Return an order-sensitive identity for the PaperInput reference list."""

    normalized = [" ".join(item.split()) for item in references]
    payload = "\n".join(normalized).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _doi(value: str) -> str:
    return value.casefold().removeprefix("https://doi.org/").removeprefix("doi:").strip()


def _arxiv(value: str) -> str:
    return value.casefold().removeprefix("arxiv:").split("v", 1)[0]


def _hit_key(hit: SearchHit) -> str:
    return _doi(hit.doi) if hit.doi else f"{hit.source_id or ''}:{hit.external_id or hit.document_id}:{_text(hit.title)}"
