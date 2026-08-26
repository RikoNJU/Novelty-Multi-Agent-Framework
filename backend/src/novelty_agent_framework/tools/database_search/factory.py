"""Composition root for structured database retrieval internals."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...persistence import ReferenceStore
from ...ports import SearchPlanner
from .providers.null_catalog import build_null_catalog_source
from .retrieval_sources import RetrievalSource, RetrievalSourceRegistry
from .structured_retrieval import StructuredSourceRetrievalTool


def build_source_registry() -> RetrievalSourceRegistry:
    registry = RetrievalSourceRegistry()
    registry.register("arxiv", _build_arxiv_source_lazily)
    registry.register("null_catalog", build_null_catalog_source)
    return registry


def _build_arxiv_source_lazily(config: Mapping[str, Any]) -> RetrievalSource:
    from .providers.arxiv import build_arxiv_source

    return build_arxiv_source(config)


def build_retrieval_source(
    retrieval: Mapping[str, Any],
    *,
    source_id: str | None = None,
    source_registry: RetrievalSourceRegistry | None = None,
) -> RetrievalSource:
    selected = (source_id or str(retrieval.get("active_source", "arxiv"))).strip().lower()
    sources = retrieval.get("sources", {})
    if not isinstance(sources, Mapping):
        raise ValueError("retrieval.sources 必须是对象映射")
    if selected not in sources:
        raise ValueError(f"活动检索来源 {selected!r} 未在 retrieval.sources 中配置")
    source_config = sources[selected]
    if not isinstance(source_config, Mapping):
        raise ValueError(f"retrieval.sources.{selected} 必须是对象映射")
    if not source_config.get("enabled", False):
        raise ValueError(f"活动检索来源 {selected!r} 已被禁用")
    return (source_registry or build_source_registry()).build(selected, source_config)


def build_structured_source_retrieval_tool(
    retrieval: Mapping[str, Any],
    *,
    search_planner: SearchPlanner,
    source_id: str | None = None,
    source_registry: RetrievalSourceRegistry | None = None,
    reference_store: ReferenceStore | None = None,
    max_concurrency: int = 4,
) -> StructuredSourceRetrievalTool:
    source = build_retrieval_source(
        retrieval, source_id=source_id, source_registry=source_registry
    )
    return StructuredSourceRetrievalTool(
        search_planner=search_planner,
        source=source,
        reference_store=reference_store,
        candidate_limit=int(retrieval.get("candidate_limit_per_task", 8)),
        full_text_limit=int(retrieval.get("full_text_limit_per_task", 8)),
        max_concurrency=max_concurrency,
    )
