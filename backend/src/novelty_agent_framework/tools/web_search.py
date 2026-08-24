"""Agent-facing Web discovery tool over a provider-neutral search backend."""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from ..persistence import ReferenceStore
from ..schemas import (
    AccessStatus,
    ResearcherToolObservation,
    SourceKind,
    SourceRecord,
    TaskResearchRequest,
    WebSearchArguments,
    WebSearchItem,
    WebSearchResult,
)
from .web_search_backend import SearchBackend, SearchHit


class WebSearchTool:
    name = "web_search"
    description = "搜索 Web 以发现候选来源；搜索结果本身不是证据。"
    args_schema = WebSearchArguments

    def __init__(
        self,
        backend: SearchBackend,
        reference_store: ReferenceStore | None = None,
    ) -> None:
        if not backend.name.strip():
            raise ValueError("search backend name cannot be empty")
        self.backend = backend
        self.reference_store = reference_store or ReferenceStore()

    async def ainvoke(
        self,
        arguments: WebSearchArguments,
        *,
        scope: TaskResearchRequest,
    ) -> ResearcherToolObservation:
        started = time.monotonic()
        backend_result = await self.backend.search(
            arguments.query,
            max_results=arguments.max_results,
        )
        observed_at = datetime.now(timezone.utc)
        manifest = self.reference_store.load_manifest(scope.subject_paper_id)
        records_by_id = {
            record.source_record_id: record for record in manifest.source_records
        }
        items: list[WebSearchItem] = []

        for rank, hit in enumerate(backend_result.hits, start=1):
            source_record_id = _source_record_id(self.backend.name, hit.url)
            current = records_by_id.get(source_record_id)
            record = _source_record(
                source_record_id=source_record_id,
                backend_name=self.backend.name,
                hit=hit,
                observed_at=observed_at,
                run_id=scope.run_id,
                query=arguments.query,
                rank=rank,
                current=current,
            )
            records_by_id[source_record_id] = record
            items.append(
                WebSearchItem(
                    source_record_id=source_record_id,
                    rank=rank,
                    title=hit.title,
                    url=hit.url,
                    snippet=hit.snippet,
                    score=hit.score,
                    published_at=hit.published_at,
                    source_name=hit.source_name,
                )
            )

        updated_manifest = manifest.model_copy(
            update={
                "source_records": list(records_by_id.values()),
                "updated_at": observed_at,
            }
        )
        self.reference_store.persist_manifest(
            scope.subject_paper_id,
            updated_manifest,
        )
        result = WebSearchResult(
            query=backend_result.query,
            results=items,
            warnings=list(backend_result.warnings),
        )
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            summary=f"发现并保存 {len(items)} 个 Web 候选来源",
            payload={"search_result": result.model_dump(mode="json")},
            elapsed_ms=int((time.monotonic() - started) * 1_000),
        )


def _source_record(
    *,
    source_record_id: str,
    backend_name: str,
    hit: SearchHit,
    observed_at: datetime,
    run_id: str,
    query: str,
    rank: int,
    current: SourceRecord | None,
) -> SourceRecord:
    raw_metadata: dict[str, Any] = (
        dict(current.raw_metadata) if current is not None else {}
    )
    raw_metadata.update(hit.raw_metadata)
    raw_metadata.update(
        {
            "search_snippet": hit.snippet,
            "search_score": hit.score,
            "published_at": (
                hit.published_at.isoformat() if hit.published_at is not None else None
            ),
            "source_name": hit.source_name,
        }
    )
    provenance = dict(current.provenance) if current is not None else {}
    provenance.update(
        {
            "tool": "web_search",
            "run_id": run_id,
            "query": query,
            "rank": rank,
        }
    )
    values = {
        "source_record_id": source_record_id,
        "work_id": current.work_id if current is not None else None,
        "source_id": backend_name,
        "source_kind": SourceKind.WEB,
        "external_id": (
            hit.external_id
            if hit.external_id is not None
            else (current.external_id if current is not None else None)
        ),
        "title": hit.title,
        "landing_url": hit.url,
        "access_status": (
            current.access_status
            if current is not None
            else AccessStatus.DISCOVERED
        ),
        "raw_metadata": raw_metadata,
        "observed_at": observed_at,
        "provenance": provenance,
    }
    if current is None:
        return SourceRecord(**values)
    return current.model_copy(update=values)


def _source_record_id(backend_name: str, url: str) -> str:
    normalized = _normalized_url(url)
    digest = hashlib.sha256(f"{backend_name}\0{normalized}".encode()).hexdigest()
    return f"src_{digest[:24]}"


def _normalized_url(url: str) -> str:
    value = url.strip()
    parts = urlsplit(value)
    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower()
    if not scheme or not hostname:
        return value
    port = parts.port
    default_port = (scheme == "http" and port == 80) or (
        scheme == "https" and port == 443
    )
    host = hostname if port is None or default_port else f"{hostname}:{port}"
    path = parts.path or "/"
    return urlunsplit((scheme, host, path, parts.query, ""))
