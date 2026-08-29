"""Formal agent-facing database_search tool."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from ...persistence import ReferenceStore
from ...schemas import (
    DatabaseSearchArguments,
    DatabaseSearchItem,
    DatabaseSearchResult,
    ResearcherToolObservation,
    StructuredSourceRetrievalRequest,
    TaskResearchRequest,
)
from .structured_retrieval import StructuredSourceRetrievalTool


class DatabaseSearchTool:
    name = "database_search"
    description = (
        "搜索已配置的结构化文献数据库并保存候选作品；候选来源本身不是证据。"
    )
    args_schema = DatabaseSearchArguments

    def __init__(
        self,
        tools_by_source: Mapping[str, StructuredSourceRetrievalTool],
        reference_store: ReferenceStore,
    ) -> None:
        normalized = {key.strip().lower(): value for key, value in tools_by_source.items()}
        if not normalized:
            raise ValueError("at least one database source is required")
        for source_id, tool in normalized.items():
            if source_id != tool.source_id:
                raise ValueError(
                    f"database source key {source_id!r} does not match tool {tool.source_id!r}"
                )
            if tool.reference_store is not reference_store:
                raise ValueError("all database retrieval tools must share reference_store")
        self.tools_by_source = normalized
        self.reference_store = reference_store

    async def ainvoke(
        self,
        arguments: DatabaseSearchArguments,
        *,
        scope: TaskResearchRequest,
    ) -> ResearcherToolObservation:
        source_id = arguments.source_id
        try:
            retrieval = self.tools_by_source[source_id]
        except KeyError as exc:
            available = ", ".join(sorted(self.tools_by_source))
            raise ValueError(
                f"database source {source_id!r} is unavailable; configured: {available}"
            ) from exc

        started = time.monotonic()
        bundle = await retrieval.ainvoke(
            StructuredSourceRetrievalRequest(
                subject_paper_id=scope.subject_paper_id,
                run_id=scope.run_id,
                source_id=source_id,
                novelty_point=scope.novelty_point,
                research_task=scope.research_task,
                search_plan=scope.search_plan,
            )
        )
        artifacts_by_record: dict[str, list[str]] = {}
        for artifact in bundle.artifacts:
            if artifact.source_record_id is not None:
                artifacts_by_record.setdefault(artifact.source_record_id, []).append(
                    artifact.artifact_id
                )
        works = {work.work_id: work for work in bundle.works}
        items: list[DatabaseSearchItem] = []
        for record in bundle.source_records:
            if record.work_id is None or record.work_id not in works:
                continue
            work = works[record.work_id]
            preview = record.abstract[:500] if record.abstract else None
            items.append(
                DatabaseSearchItem(
                    source_record_id=record.source_record_id,
                    work_id=work.work_id,
                    title=work.title,
                    authors=work.authors,
                    publication_year=work.publication_year,
                    source_id=record.source_id,
                    access_status=record.access_status,
                    artifact_ids=sorted(artifacts_by_record.get(record.source_record_id, [])),
                    abstract_preview=preview,
                )
            )
        result = DatabaseSearchResult(
            source_id=source_id,
            results=items,
            warnings=bundle.warnings,
        )
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            summary=f"数据库检索召回 {len(items)} 个候选作品",
            payload={
                "research_bundle": bundle.model_dump(mode="json"),
                "database_search_result": result.model_dump(mode="json"),
                "search_executions": [
                    item.model_dump(mode="json") for item in bundle.search_executions
                ],
                "source_records": [
                    item.model_dump(mode="json") for item in bundle.source_records
                ],
                "artifacts": [item.model_dump(mode="json") for item in bundle.artifacts],
            },
            elapsed_ms=int((time.monotonic() - started) * 1_000),
        )

    def project_model_context(
        self, observation: ResearcherToolObservation
    ) -> dict[str, Any]:
        result = observation.payload["database_search_result"]
        return {
            "succeeded": observation.succeeded,
            "summary": observation.summary,
            "source_id": result["source_id"],
            "results": result["results"],
            "warnings": result["warnings"],
        }
