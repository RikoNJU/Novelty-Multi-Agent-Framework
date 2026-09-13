"""arXiv 数据源工具：检索、全文获取与元数据核验。

三个工具共用同一套 document_id 约定：arXiv ID 去掉 ``v<n>`` 版本后缀，
保证 SearchTool / FullTextTool / MetadataTool 之间标识自洽。
"""

from __future__ import annotations

import re
import threading
import time
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from typing import Any
from html.parser import HTMLParser
from urllib.parse import urlencode

import httpx
import pymupdf

from ....ports import FullText, FullTextTool, MetadataTool, SearchHit, SearchTool
from ....schemas import (
    EvidenceSource,
    ExternalIdentifier,
    ParsedCitation,
    SearchConcept,
)
from ..adapter import QueryAdapter, QueryAdapterError
from ..retrieval_sources import RetrievalSource

ARXIV_QUERY_URL = "https://export.arxiv.org/api/query"
ARXIV_ABS_URL = "https://arxiv.org/abs/"
ARXIV_HTML_URL = "https://arxiv.org/html/"
ARXIV_PDF_URL = "https://arxiv.org/pdf/"

ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"

_VERSION_RE = re.compile(r"v\d+$")

# arXiv 按来源 IP 限流（约每 3 秒一次请求）。工作流、bootstrap CLI 以及多来源
# 会各自构建 ArxivSearchTool 实例；若各自计时，叠加速率就会超限并触发 429，
# 因此节流状态放到模块级共享。
_THROTTLE_LOCK = threading.Lock()
_LAST_REQUEST_AT = 0.0

# 429 是限流（重试即可），5xx 是服务端瞬时故障；其余 4xx 是请求本身有问题。
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
_MAX_RETRY_DELAY_SECONDS = 60.0


def _is_retryable(status_code: int) -> bool:
    return status_code in _RETRYABLE_STATUS


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    """优先遵守 Retry-After，否则指数退避（2s、4s、8s…），并设上限。"""

    header = (response.headers.get("Retry-After") or "").strip()
    if header.isdigit():
        return min(float(header), _MAX_RETRY_DELAY_SECONDS)
    return min(2.0 * (2**attempt), _MAX_RETRY_DELAY_SECONDS)


class ArxivQueryAdapter(QueryAdapter):
    """把通用检索 Concept 编译为 arXiv ``all:`` 查询。"""

    database = "arxiv"

    def __init__(self, *, render_v2: bool = True, phrase_max_words: int = 3) -> None:
        self.render_v2 = render_v2
        self.phrase_max_words = phrase_max_words

    def _render_concept(
        self,
        concept: SearchConcept,
        *,
        use_alias: bool = False,
        use_exclude: bool = True,
    ) -> str:
        terms: list[str] = []
        seen: set[str] = set()
        for raw_term in concept.terms:
            term = " ".join(raw_term.split())
            if not term:
                raise QueryAdapterError(f"Concept {concept.concept_id} 包含空 term")
            if term not in seen:
                seen.add(term)
                terms.append(term)
        field = _field_for_role(concept.role)
        rendered = [
            render_arxiv_term(
                term,
                render_v2=self.render_v2,
                phrase_max_words=self.phrase_max_words,
                field=field,
            )
            for term in terms
        ]
        if use_alias:
            for raw_alias in concept.alias:
                alias = " ".join(raw_alias.split())
                if alias and alias not in seen:
                    seen.add(alias)
                    rendered.append(
                        render_arxiv_term(
                            alias,
                            render_v2=self.render_v2,
                            phrase_max_words=self.phrase_max_words,
                            field=field,
                        )
                    )
        block = rendered[0] if len(rendered) == 1 else f"({' OR '.join(rendered)})"
        excluded = [
            render_arxiv_term(
                " ".join(raw.split()),
                render_v2=self.render_v2,
                phrase_max_words=self.phrase_max_words,
                field="all",
            )
            for raw in concept.exclude
            if raw.strip()
        ]
        if use_exclude and excluded:
            block = f"{block} ANDNOT ({' OR '.join(excluded)})"
        return block


def _field_for_role(role: str | None) -> str:
    """按概念角色选择 arXiv 字段：object 标题优先，方法/特征用摘要，
    escape 用全字段，缺省（v1 兼容）用 all。
    """

    if role == "escape":
        return "all"
    if role == "object":
        return "ti"
    if role in ("method", "feature", "setting"):
        return "abs"
    return "all"


def render_arxiv_term(
    term: str,
    *,
    render_v2: bool = True,
    phrase_max_words: int = 3,
    field: str = "all",
) -> str:
    """把单个术语渲染为 arXiv all: 查询片段（纯函数，可单测）。

    - render_v2=False：始终 quoted phrase（all:"term"，v1 行为）；
    - render_v2=True：词数 <= phrase_max_words 保持 quoted phrase；
      词数更多时拆成词级 AND（all:w1 AND all:w2 ...），词级模式会
      剥离术语内嵌的双引号（引号只在短语内有意义）。
    """

    normalized = " ".join(term.split())
    if not normalized:
        raise ValueError("term is empty")
    if not render_v2:
        return f'{field}:"{_escape_query_term(normalized)}"'
    words = [token.strip('"') for token in normalized.split() if token.strip('"')]
    if len(words) <= phrase_max_words:
        return f'{field}:"{_escape_query_term(normalized)}"'
    return " AND ".join(f"{field}:{_escape_query_term(word)}" for word in words)


def _escape_query_term(term: str) -> str:
    return term.replace("\\", "\\\\").replace('"', '\\"')


def strip_version(arxiv_id: str) -> str:
    """去掉 arXiv ID 的版本后缀，如 ``2305.12345v2`` -> ``2305.12345``。"""

    return _VERSION_RE.sub("", arxiv_id)


def _clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def parse_entry(entry: ET.Element) -> SearchHit:
    """把 Atom entry 映射为 SearchHit。"""

    entry_id = entry.findtext(f"{ATOM_NS}id") or ""
    external_id = entry_id.rsplit("/", 1)[-1]
    arxiv_id = strip_version(external_id)
    authors = tuple(
        name.text.strip()
        for name in entry.findall(f"{ATOM_NS}author/{ATOM_NS}name")
        if name.text and name.text.strip()
    )
    published = entry.findtext(f"{ATOM_NS}published") or ""
    return SearchHit(
        document_id=arxiv_id,
        title=_clean_title(entry.findtext(f"{ATOM_NS}title") or ""),
        abstract=(entry.findtext(f"{ATOM_NS}summary") or "").strip(),
        authors=authors,
        year=int(published[:4]) if len(published) >= 4 else None,
        doi=entry.findtext(f"{ARXIV_NS}doi"),
        url=f"{ARXIV_ABS_URL}{arxiv_id}",
        source_id="arxiv",
        external_id=external_id,
        full_text_url=f"{ARXIV_PDF_URL}{arxiv_id}",
        raw_metadata={"atom_id": entry_id, "published": published},
    )


class ArxivSearchTool(SearchTool):
    """arXiv 检索薄适配器：单查询、Atom 解析、3 秒限流、5xx 重试。"""

    source_id = "arxiv"

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        base_url: str = ARXIV_QUERY_URL,
        min_interval: float = 3.0,
        timeout: float = 20.0,
        max_retries: int = 2,
    ) -> None:
        self._client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self._base_url = base_url
        self._min_interval = min_interval
        self._max_retries = max_retries

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]:
        params = urlencode({"search_query": query, "start": 0, "max_results": limit})
        response = self._get(f"{self._base_url}?{params}")
        root = ET.fromstring(response.text)
        return [parse_entry(entry) for entry in root.findall(f"{ATOM_NS}entry")]

    def resolve_identifier(self, identifier: ExternalIdentifier) -> SearchHit | None:
        """按精确 arXiv ID 解析单篇文献；非 arxiv 命名空间返回 None。"""

        if identifier.namespace != "arxiv":
            return None
        hits = self.search(f"id:{strip_version(identifier.value)}", limit=2)
        target = strip_version(identifier.value).casefold()
        return next(
            (hit for hit in hits if strip_version(hit.document_id).casefold() == target),
            None,
        )

    def search_known_item(
        self, citation: ParsedCitation, *, limit: int = 5
    ) -> Sequence[SearchHit]:
        """按引文已知项检索：优先精确 arXiv ID，否则退回标题检索。"""

        if citation.arxiv_id:
            hit = self.resolve_identifier(
                ExternalIdentifier(namespace="arxiv", value=citation.arxiv_id)
            )
            return [hit] if hit else []
        if not citation.title:
            return []
        escaped = _escape_query_term(citation.title)
        return self.search(f'ti:"{escaped}"', limit=limit)

    def _throttle(self) -> None:
        """全进程共享的节流：多个 ArxivSearchTool 实例（工作流、bootstrap、
        多来源）不再各自计时，否则叠加起来的请求速率会超过 arXiv 的单实例限制。
        """

        global _LAST_REQUEST_AT
        with _THROTTLE_LOCK:
            elapsed = time.monotonic() - _LAST_REQUEST_AT
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            _LAST_REQUEST_AT = time.monotonic()

    def _get(self, url: str) -> httpx.Response:
        # 每次尝试都重新节流：重试不能绕过速率限制，否则退避反而加剧限流。
        for attempt in range(self._max_retries + 1):
            self._throttle()
            response = self._client.get(url)
            try:
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError:
                if attempt >= self._max_retries or not _is_retryable(response.status_code):
                    raise
                time.sleep(_retry_delay(response, attempt))
        raise AssertionError("unreachable")


class _HTMLTextExtractor(HTMLParser):
    """剥离 script/style 并保留正文文本的简易 HTML 解析器。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip_depth += 1
        elif tag in ("p", "section", "div", "li", "br", "h1", "h2", "h3", "h4"):
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self._skip_depth:
            self._skip_depth -= 1
        elif tag in ("p", "section", "div", "li", "h1", "h2", "h3", "h4"):
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._parts.append(data)

    def text(self) -> str:
        raw = "".join(self._parts)
        return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+\n", "\n", raw)).strip()


class ArxivFullTextTool(FullTextTool):
    """arXiv 全文获取：HTML 优先，PDF（PyMuPDF）兜底，失败返回 None。"""

    source_id = "arxiv"

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        timeout: float = 30.0,
        max_chars: int = 100_000,
    ) -> None:
        self._client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self._max_chars = max_chars
        self._cache: dict[str, FullText | None] = {}

    def fetch(self, document_id: str) -> FullText | None:
        doc_id = strip_version(document_id)
        if doc_id in self._cache:
            return self._cache[doc_id]
        result = self._fetch_html(doc_id) or self._fetch_pdf(doc_id)
        self._cache[doc_id] = result
        return result

    def _fetch_html(self, doc_id: str) -> FullText | None:
        response = self._try_get(f"{ARXIV_HTML_URL}{doc_id}")
        if response is None:
            return None
        extractor = _HTMLTextExtractor()
        try:
            extractor.feed(response.text)
            text = extractor.text()
        except Exception:
            return None
        if not text:
            return None
        title = self._html_title(response.text) or doc_id
        return self._make_full_text(
            doc_id, title, text, source_url=f"{ARXIV_HTML_URL}{doc_id}"
        )

    def _fetch_pdf(self, doc_id: str) -> FullText | None:
        response = self._try_get(f"{ARXIV_PDF_URL}{doc_id}")
        if response is None:
            return None
        try:
            document = pymupdf.open(stream=response.content, filetype="pdf")
        except Exception:
            return None
        try:
            text = "\n".join(page.get_text() for page in document)
        finally:
            document.close()
        if not text.strip():
            return None
        return self._make_full_text(
            doc_id, doc_id, text, source_url=f"{ARXIV_PDF_URL}{doc_id}"
        )

    def _make_full_text(
        self, doc_id: str, title: str, text: str, *, source_url: str
    ) -> FullText:
        truncated = len(text) > self._max_chars
        return FullText(
            document_id=doc_id,
            title=title,
            text=text[: self._max_chars],
            source=EvidenceSource(title=title, url=f"{ARXIV_ABS_URL}{doc_id}"),
            media_type="text/plain",
            content_extent="partial" if truncated else "unknown",
            source_url=source_url,
        )

    def _try_get(self, url: str) -> httpx.Response | None:
        try:
            response = self._client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPError:
            return None

    @staticmethod
    def _html_title(text: str) -> str | None:
        match = re.search(r"<title[^>]*>(.*?)</title>", text, re.DOTALL | re.IGNORECASE)
        if match is None:
            return None
        title = re.sub(r"<[^>]+>", "", match.group(1))
        return _clean_title(title) or None


class ArxivMetadataTool(MetadataTool):
    """arXiv 元数据核验：用 id_list 精确查询，返回规范 EvidenceSource。"""

    source_id = "arxiv"

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        base_url: str = ARXIV_QUERY_URL,
        timeout: float = 20.0,
    ) -> None:
        self._client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self._base_url = base_url
        self._cache: dict[str, EvidenceSource | None] = {}

    def resolve(self, document_id: str) -> EvidenceSource | None:
        doc_id = strip_version(document_id)
        if doc_id in self._cache:
            return self._cache[doc_id]
        result = self._resolve_live(doc_id)
        self._cache[doc_id] = result
        return result

    def _resolve_live(self, doc_id: str) -> EvidenceSource | None:
        try:
            response = self._client.get(
                f"{self._base_url}?id_list={doc_id}&max_results=1"
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return None
        try:
            root = ET.fromstring(response.text)
            entries = root.findall(f"{ATOM_NS}entry")
        except ET.ParseError:
            return None
        if not entries:
            return None
        hit = parse_entry(entries[0])
        return EvidenceSource(title=hit.title, doi=hit.doi, url=hit.url)


def build_arxiv_source(config: Mapping[str, Any]) -> RetrievalSource:
    """从来源专用配置构建自洽的 arXiv 能力包。"""

    enabled = bool(config.get("enabled", False))
    render_v2 = bool(config.get("render_v2", True))
    if not enabled or config.get("adapter_only", False):
        return RetrievalSource(
            source_id="arxiv",
            query_adapter=ArxivQueryAdapter(render_v2=render_v2),
        )
    timeout_seconds = float(config["timeout_seconds"])
    client = httpx.Client(timeout=timeout_seconds, follow_redirects=True)
    return RetrievalSource(
        source_id="arxiv",
        query_adapter=ArxivQueryAdapter(render_v2=render_v2),
        search_tool=ArxivSearchTool(
            client=client,
            min_interval=float(config["min_interval_seconds"]),
            max_retries=int(config["max_retries"]),
        ),
        full_text_tool=ArxivFullTextTool(
            client=client, max_chars=int(config["full_text_max_chars"])
        ),
        metadata_tool=ArxivMetadataTool(client=client),
    )
