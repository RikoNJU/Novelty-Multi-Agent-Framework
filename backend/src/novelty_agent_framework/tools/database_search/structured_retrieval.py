"""单任务级结构化来源检索、读取与参考文献入库工具。"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import re
from collections.abc import Awaitable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, TypeVar, cast

from ...persistence import ReferenceStore
from ...ports import FullText, SearchHit, SearchPlanner
from ...schemas import (
    AccessStatus,
    Artifact,
    ArtifactRole,
    ContentExtent,
    ExternalIdentifier,
    ReferenceManifest,
    ResearchBundle,
    SearchExecution,
    SearchExecutionStatus,
    SearchPlan,
    SearchResultRef,
    SourceKind,
    SourceRecord,
    StructuredSourceRetrievalRequest,
    Work,
    WorkType,
)
from .adapter import CompiledQuery
from .retrieval_sources import RetrievalSource

T = TypeVar("T")


async def _resolve(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await cast(Awaitable[T], value)
    return value


@dataclass
class _PendingExecution:
    execution_id: str
    query: CompiledQuery
    started_at: datetime
    completed_at: datetime
    hits: list[SearchHit]


class StructuredRetrievalAdapter:
    """把现有端口对象映射为稳定的参考文献数据模型。"""

    @staticmethod
    def stable_id(prefix: str, *parts: str) -> str:
        payload = "\x1f".join(parts).encode("utf-8")
        return f"{prefix}_{hashlib.sha256(payload).hexdigest()[:24]}"

    def adapt_hit(
        self, hit: SearchHit, source_id: str, observed_at: datetime
    ) -> tuple[Work, SourceRecord, list[str]]:
        external_id = (hit.external_id or hit.document_id).strip()
        warnings: list[str] = []
        identifiers: list[ExternalIdentifier] = []
        if (
            source_id == "arxiv"
            and hit.document_id
            and external_id == hit.document_id
        ):
            warnings.append(
                f"arxiv record {hit.document_id} has no observed version; v1 was not inferred"
            )
        if hit.doi:
            identifiers.append(ExternalIdentifier(namespace="doi", value=hit.doi))
            work_key = f"doi:{_normalize_doi(hit.doi)}"
        elif source_id == "arxiv" and hit.document_id:
            identifiers.append(
                ExternalIdentifier(namespace="arxiv", value=hit.document_id)
            )
            work_key = f"arxiv:{hit.document_id}"
        elif external_id:
            work_key = f"{source_id}:{external_id}"
        else:
            fingerprint = "|".join(
                [
                    _normalize_text(hit.title),
                    "|".join(_normalize_text(author) for author in hit.authors),
                    str(hit.year or ""),
                ]
            )
            work_key = f"fingerprint:{fingerprint}"
            warnings.append(
                f"candidate {hit.title!r} uses a title/author/year fallback fingerprint"
            )
        work_id = self.stable_id("wrk", work_key)
        record_id = self.stable_id("src", source_id, external_id or work_key)
        work = Work(
            work_id=work_id,
            work_type=WorkType.ARTICLE,
            title=hit.title,
            authors=list(hit.authors),
            publication_year=hit.year,
            identifiers=identifiers,
        )
        record = SourceRecord(
            source_record_id=record_id,
            work_id=work_id,
            source_id=source_id,
            source_kind=SourceKind.STRUCTURED_DATABASE,
            external_id=external_id or None,
            title=hit.title,
            authors=list(hit.authors),
            abstract=hit.abstract or None,
            publication_year=hit.year,
            identifiers=list(identifiers),
            landing_url=hit.url,
            full_text_url=hit.full_text_url,
            access_status=(
                AccessStatus.METADATA_ONLY
                if hit.abstract
                else AccessStatus.DISCOVERED
            ),
            raw_metadata=hit.raw_metadata,
            observed_at=observed_at,
            provenance={
                "adapter": "structured_retrieval",
                "identity_basis": work_key.split(":", 1)[0],
            },
        )
        return work, record, warnings


class StructuredSourceRetrievalTool:
    """Injected SearchPlan → RetrievalSource → Metadata/FullText → ResearchBundle。"""

    name = "structured_source_retrieval"

    def __init__(
        self,
        *,
        search_planner: SearchPlanner | None = None,
        source: RetrievalSource,
        reference_store: ReferenceStore | None = None,
        candidate_limit: int = 8,
        full_text_limit: int = 8,
        max_concurrency: int = 4,
    ) -> None:
        if source.query_adapter is None:
            raise ValueError("RetrievalSource.query_adapter is required")
        if source.search_tool is None:
            raise ValueError("RetrievalSource.search_tool is required")
        if candidate_limit < 1 or full_text_limit < 0 or max_concurrency < 1:
            raise ValueError("retrieval limits and concurrency are invalid")
        # LEGACY / UNUSED: 旧版会在数据库检索阶段再次调用 Planner。
        # 当前正式链由 TaskResearchRequest.search_plan 注入唯一计划。
        # 仅为历史构造器兼容保留；新代码禁止依赖。
        self.search_planner = search_planner
        self.source = source
        self.reference_store = reference_store or ReferenceStore()
        self.candidate_limit = candidate_limit
        self.full_text_limit = full_text_limit
        self.max_concurrency = max_concurrency
        self.source_id = source.source_id
        self.adapter = StructuredRetrievalAdapter()

    async def ainvoke(
        self, request: StructuredSourceRetrievalRequest
    ) -> ResearchBundle:
        request = StructuredSourceRetrievalRequest.model_validate(request)
        if request.source_id != self.source_id:
            raise ValueError(
                f"request source_id {request.source_id!r} does not match "
                f"tool source_id {self.source_id!r}"
            )
        manifest = self.reference_store.load_manifest(request.subject_paper_id)
        plan = request.search_plan
        compiled, warnings = self._compile_strategies(plan)
        pending, failed, unique_hits = await self._search(compiled, request)
        enriched_hits, acquisition_warnings = await self._enrich_metadata(unique_hits)
        warnings.extend(acquisition_warnings)

        observed_at = datetime.now(timezone.utc)
        mapped: dict[str, tuple[Work, SourceRecord]] = {}
        works: dict[str, Work] = {}
        records: dict[str, SourceRecord] = {}
        for key, hit in enriched_hits.items():
            try:
                work, record, hit_warnings = self.adapter.adapt_hit(
                    hit, self.source_id, observed_at
                )
            except Exception as exc:
                warnings.append(
                    f"candidate {hit.document_id or hit.title!r} could not be mapped: {_safe_error(exc)}"
                )
                continue
            warnings.extend(hit_warnings)
            _merge_work(works, work)
            _merge_record(records, record)
            mapped[key] = (work, record)

        executions = [*failed]
        for item in pending:
            results: list[SearchResultRef] = []
            seen_records: set[str] = set()
            partial = False
            for rank, original_hit in enumerate(item.hits, start=1):
                pair = mapped.get(_candidate_key(original_hit))
                if pair is None:
                    partial = True
                    continue
                record_id = pair[1].source_record_id
                if record_id in seen_records:
                    partial = True
                    warnings.append(
                        f"search execution {item.execution_id} returned duplicate source record {record_id}"
                    )
                    continue
                seen_records.add(record_id)
                results.append(SearchResultRef(source_record_id=record_id, rank=rank))
            executions.append(
                SearchExecution(
                    execution_id=item.execution_id,
                    run_id=request.run_id,
                    tool_name=self.name,
                    source_id=self.source_id,
                    query=item.query.query,
                    parameters=_query_parameters(item.query, self.candidate_limit),
                    status=(
                        SearchExecutionStatus.PARTIAL
                        if partial
                        else SearchExecutionStatus.SUCCEEDED
                    ),
                    started_at=item.started_at,
                    completed_at=item.completed_at,
                    results=results,
                )
            )

        artifacts: dict[str, Artifact] = {}
        for key, hit in enriched_hits.items():
            pair = mapped.get(key)
            if pair is None or not hit.abstract.strip():
                continue
            work, record = pair
            artifact = self._try_save_artifact(
                request.subject_paper_id,
                work=work,
                record=record,
                role=ArtifactRole.ABSTRACT,
                content=hit.abstract,
                extent=ContentExtent.FULL,
                provenance={"source": "search_hit.abstract"},
                warnings=warnings,
            )
            if artifact is not None:
                artifacts[artifact.artifact_id] = artifact

        full_texts, full_text_warnings = await self._fetch_full_texts(
            list(enriched_hits.items())[: self.full_text_limit]
        )
        warnings.extend(full_text_warnings)
        if self.source.full_text_tool is None and any(
            hit.abstract.strip() for hit in enriched_hits.values()
        ):
            warnings.append(
                "full_text_tool is unavailable; saved abstracts only"
            )
        for key, full_text in full_texts.items():
            pair = mapped.get(key)
            if pair is None or not full_text.text.strip():
                continue
            work, record = pair
            try:
                extent = ContentExtent(full_text.content_extent)
            except ValueError:
                extent = ContentExtent.UNKNOWN
                warnings.append(
                    f"full text {full_text.document_id} has invalid content_extent; unknown was used"
                )
            artifact = self._try_save_artifact(
                request.subject_paper_id,
                work=work,
                record=record,
                role=ArtifactRole.EXTRACTED_TEXT,
                content=full_text.text,
                extent=extent,
                version_label=full_text.version_label,
                provenance={
                    "source": "full_text_tool",
                    "source_url": full_text.source_url,
                    "media_type_received": full_text.media_type,
                },
                warnings=warnings,
            )
            if artifact is not None:
                artifacts[artifact.artifact_id] = artifact
                records[record.source_record_id] = record.model_copy(
                    update={"access_status": AccessStatus.FULL_TEXT_ACQUIRED}
                )

        merged = _merge_manifest(
            manifest,
            list(works.values()),
            list(records.values()),
            list(artifacts.values()),
        )
        self.reference_store.persist_manifest(request.subject_paper_id, merged)
        return ResearchBundle(
            bundle_id=self.adapter.stable_id(
                "bnd",
                request.subject_paper_id,
                request.run_id or "",
                request.research_task.novelty_point_id,
                request.research_task.task_id,
                self.source_id,
            ),
            producer=f"{self.name}:{self.source_id}",
            search_executions=sorted(
                executions, key=lambda value: value.started_at
            ),
            works=list(works.values()),
            source_records=list(records.values()),
            artifacts=list(artifacts.values()),
            evidence=[],
            warnings=list(dict.fromkeys(warnings)),
        )

    def invoke(
        self, request: StructuredSourceRetrievalRequest
    ) -> ResearchBundle:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.ainvoke(request))
        raise RuntimeError(
            "检测到正在运行的事件循环，请改用 await tool.ainvoke(...)"
        )

    def _compile_strategies(
        self, plan: SearchPlan
    ) -> tuple[list[CompiledQuery], list[str]]:
        compiled: list[CompiledQuery] = []
        warnings: list[str] = []
        for strategy in plan.strategies:
            single = plan.model_copy(update={"strategies": [strategy]})
            try:
                compiled.extend(self.source.query_adapter.compile(single))
            except Exception as exc:
                warnings.append(
                    f"query compilation {plan.novelty_point_id}/{plan.task_id}/{strategy.strategy_id} failed: {_safe_error(exc)}"
                )
        return compiled, warnings

    async def _search(
        self,
        compiled: Sequence[CompiledQuery],
        request: StructuredSourceRetrievalRequest,
    ) -> tuple[
        list[_PendingExecution], list[SearchExecution], dict[str, SearchHit]
    ]:
        pending: list[_PendingExecution] = []
        failed: list[SearchExecution] = []
        unique: dict[str, SearchHit] = {}
        for index, query in enumerate(compiled, start=1):
            started = datetime.now(timezone.utc)
            execution_id = self.adapter.stable_id(
                "sex",
                request.run_id or request.subject_paper_id,
                request.research_task.task_id,
                query.strategy_id,
                query.query,
                str(index),
            )
            try:
                raw_hits = list(
                    await _resolve(
                        self.source.search_tool.search(
                            query.query, limit=self.candidate_limit
                        )
                    )
                )
                hits = [
                    hit if isinstance(hit, SearchHit) else SearchHit(**hit)
                    for hit in raw_hits
                ]
            except Exception as exc:
                failed.append(
                    SearchExecution(
                        execution_id=execution_id,
                        run_id=request.run_id,
                        tool_name=self.name,
                        source_id=self.source_id,
                        query=query.query,
                        parameters=_query_parameters(query, self.candidate_limit),
                        status=SearchExecutionStatus.FAILED,
                        started_at=started,
                        completed_at=datetime.now(timezone.utc),
                        error=_safe_error(exc),
                    )
                )
                continue
            pending.append(
                _PendingExecution(
                    execution_id=execution_id,
                    query=query,
                    started_at=started,
                    completed_at=datetime.now(timezone.utc),
                    hits=hits,
                )
            )
            for hit in hits:
                unique.setdefault(_candidate_key(hit), hit)
            if len(unique) >= self.candidate_limit:
                break
        return pending, failed, dict(list(unique.items())[: self.candidate_limit])

    async def _enrich_metadata(
        self, hits: Mapping[str, SearchHit]
    ) -> tuple[dict[str, SearchHit], list[str]]:
        if self.source.metadata_tool is None:
            return dict(hits), []
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def enrich(key: str, hit: SearchHit) -> tuple[str, SearchHit, str | None]:
            async with semaphore:
                try:
                    metadata = await _resolve(
                        self.source.metadata_tool.resolve(hit.document_id)
                    )
                except Exception as exc:
                    return key, hit, f"metadata {hit.document_id}: {_safe_error(exc)}"
            if metadata is None:
                return key, hit, None
            return key, replace(
                hit,
                title=metadata.title or hit.title,
                doi=metadata.doi or hit.doi,
                url=metadata.url or hit.url,
            ), None

        results = await asyncio.gather(
            *(enrich(key, hit) for key, hit in hits.items())
        )
        return (
            {key: hit for key, hit, _ in results},
            [warning for _, _, warning in results if warning is not None],
        )

    async def _fetch_full_texts(
        self, hits: Sequence[tuple[str, SearchHit]]
    ) -> tuple[dict[str, FullText], list[str]]:
        if self.source.full_text_tool is None:
            return {}, []
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def fetch(key: str, hit: SearchHit) -> tuple[str, FullText | None, str | None]:
            async with semaphore:
                try:
                    value = await _resolve(
                        self.source.full_text_tool.fetch(hit.document_id)
                    )
                    return key, value, None
                except Exception as exc:
                    return key, None, f"full text {hit.document_id}: {_safe_error(exc)}"

        results = await asyncio.gather(*(fetch(key, hit) for key, hit in hits))
        return (
            {key: value for key, value, _ in results if value is not None},
            [
                warning
                for _, _, warning in results
                if warning is not None
            ]
            + [
                f"full text {hit.document_id}: no content returned; abstract only"
                for (key, hit), (result_key, value, warning) in zip(hits, results)
                if key == result_key and value is None and warning is None
            ],
        )

    def _try_save_artifact(
        self,
        paper_id: str,
        *,
        work: Work,
        record: SourceRecord,
        role: ArtifactRole,
        content: str,
        extent: ContentExtent,
        provenance: dict[str, Any],
        warnings: list[str],
        version_label: str | None = None,
    ) -> Artifact | None:
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        artifact_id = self.adapter.stable_id(
            "art", work.work_id, role.value, digest
        )
        try:
            self.reference_store.write_document(
                paper_id,
                work_id=work.work_id,
                artifact_id=artifact_id,
                extension="txt",
                content=content,
            )
        except Exception as exc:
            warnings.append(
                f"artifact {artifact_id} could not be saved: {_safe_error(exc)}"
            )
            return None
        return Artifact(
            artifact_id=artifact_id,
            work_id=work.work_id,
            source_record_id=record.source_record_id,
            role=role,
            media_type="text/plain",
            relative_path=f"documents/{work.work_id}/{artifact_id}.txt",
            sha256=digest,
            byte_size=len(content.encode("utf-8")),
            version_label=version_label,
            content_extent=extent,
            acquired_at=datetime.now(timezone.utc),
            provenance=provenance,
        )


def _merge_manifest(
    manifest: ReferenceManifest,
    works: Sequence[Work],
    records: Sequence[SourceRecord],
    artifacts: Sequence[Artifact],
) -> ReferenceManifest:
    work_map = {item.work_id: item for item in manifest.works}
    record_map = {item.source_record_id: item for item in manifest.source_records}
    artifact_map = {item.artifact_id: item for item in manifest.artifacts}
    for work in works:
        _merge_work(work_map, work)
    for record in records:
        _merge_record(record_map, record)
    for artifact in artifacts:
        existing = artifact_map.get(artifact.artifact_id)
        if existing is not None and (
            existing.work_id != artifact.work_id
            or existing.sha256 != artifact.sha256
            or existing.relative_path != artifact.relative_path
        ):
            raise ValueError(f"artifact {artifact.artifact_id} conflicts with manifest")
        artifact_map.setdefault(artifact.artifact_id, artifact)
    return ReferenceManifest(
        schema_version=manifest.schema_version,
        subject_paper_id=manifest.subject_paper_id,
        updated_at=datetime.now(timezone.utc),
        works=list(work_map.values()),
        source_records=list(record_map.values()),
        artifacts=list(artifact_map.values()),
    )


def _merge_work(target: dict[str, Work], value: Work) -> None:
    existing = target.get(value.work_id)
    if existing is None:
        target[value.work_id] = value


def _merge_record(target: dict[str, SourceRecord], value: SourceRecord) -> None:
    existing = target.get(value.source_record_id)
    if existing is None:
        target[value.source_record_id] = value
        return
    if existing.work_id != value.work_id or existing.source_id != value.source_id:
        raise ValueError(f"source_record {value.source_record_id} has identity conflict")
    if value.access_status == AccessStatus.FULL_TEXT_ACQUIRED:
        target[value.source_record_id] = existing.model_copy(
            update={"access_status": value.access_status}
        )


def _candidate_key(hit: SearchHit) -> str:
    external_id = (hit.external_id or hit.document_id).strip()
    if external_id:
        return f"source:{hit.source_id or ''}:{external_id}"
    if hit.doi:
        return f"doi:{_normalize_doi(hit.doi)}"
    if hit.url:
        return f"url:{hit.url.casefold().rstrip('/')}"
    return f"title:{_normalize_text(hit.title)}"


def _query_parameters(query: CompiledQuery, limit: int) -> dict[str, Any]:
    return {
        "limit": limit,
        "task_id": query.task_id,
        "novelty_point_id": query.novelty_point_id,
        "strategy_id": query.strategy_id,
        "level": query.level,
    }


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def _normalize_doi(value: str) -> str:
    normalized = value.strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if normalized.startswith(prefix):
            return normalized[len(prefix) :].strip()
    return normalized


def _safe_error(exc: Exception) -> str:
    message = re.sub(
        r"(?i)(api[_-]?key|authorization|cookie)\s*[:=]\s*\S+",
        r"\1=<redacted>",
        str(exc),
    )
    return f"{type(exc).__name__}: {message}"[:1000]
