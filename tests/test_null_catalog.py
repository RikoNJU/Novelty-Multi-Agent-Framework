"""arXiv 与 null_catalog 在同一注入位置竞争，active_source 只有一个赢家。"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest
from backend.env import ModelResponse, ModelToolCall

from novelty_agent_framework.agents import (
    DemoCoordinator,
    DemoPointExtractor,
    DemoSearchPlanner,
)
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.config import build_retrieval_source
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.schemas import (
    CallToolAction,
    FinishResearchAction,
    PaperInput,
    SearchConcept,
    SearchPlan,
    SearchStrategy,
)
from novelty_agent_framework.tools import (
    EvidenceCardBuilder,
    ResearcherToolRegistry,
)
from novelty_agent_framework.tools.database_search import (
    NullQueryAdapter,
    NullSearchTool,
    RetrievalSource,
    RetrievalSourceRegistry,
    StructuredSourceRetrievalTool,
    StructuredRetrievalResearcherTool,
)
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivQueryAdapter
from novelty_agent_framework.tools.database_search.providers.null_catalog import (
    build_null_catalog_source,
)
from novelty_agent_framework.workflows import (
    NoveltyWorkflow,
    NoveltyWorkflowConfig,
    NoveltyWorkflowServices,
    TaskResearcherWorkflow,
)


def _config(active_source: str) -> dict[str, Any]:
    return {
        "retrieval": {
            "active_source": active_source,
            "candidate_limit_per_task": 8,
            "sources": {
                "arxiv": {"enabled": True},
                "null_catalog": {"enabled": True, "testing_only": True},
            },
        }
    }


def _paper() -> PaperInput:
    return PaperInput(
        paper_id="null-source-test",
        title="Source selection",
        abstract="Explicit source selection",
        full_text="Explicit source selection must not depend on task language.",
        claimed_contributions=["A source-independent retrieval workflow"],
    )


def _workflow(source: RetrievalSource) -> NoveltyWorkflow:
    class RetrieveThenFinishModel:
        async def acomplete(self, messages, *, options=None):
            if not any(message.role == "tool" for message in messages):
                return ModelResponse(content=None, tool_calls=[ModelToolCall(
                    id="retrieval-call", name="structured_source_retrieval",
                    arguments={"source_id": source.source_id})])
            return ModelResponse(content=json.dumps(
                {"cards": [], "no_evidence_reason": "catalog is empty"}))

    store = ReferenceStore()
    retrieval = StructuredSourceRetrievalTool(
        search_planner=DemoSearchPlanner(),
        source=source,
        reference_store=store,
    )
    task_researcher = TaskResearcherWorkflow(
        RetrieveThenFinishModel(),
        ResearcherToolRegistry(
            [StructuredRetrievalResearcherTool({source.source_id: retrieval})]
        ),
        EvidenceCardBuilder(store),
    )
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            task_researcher=task_researcher,
            search_planner=DemoSearchPlanner(),
            point_extractor=DemoPointExtractor(),
        ),
        NoveltyWorkflowConfig(max_rounds=1),
    )


class StubArxivSearchTool:
    source_id = "arxiv"

    def __init__(self) -> None:
        self.queries: list[str] = []

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]:
        self.queries.append(query)
        return ()


def _stub_arxiv_builder(config: Mapping[str, Any]) -> RetrievalSource:
    return RetrievalSource(
        source_id="arxiv",
        query_adapter=ArxivQueryAdapter(),
        search_tool=StubArxivSearchTool(),
    )


def _forbidden_builder(name: str):
    def build(config: Mapping[str, Any]) -> RetrievalSource:
        raise AssertionError(f"未选中的 {name} builder 不应被调用")

    return build


def test_null_catalog_replaces_arxiv_without_fallback(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    registry = RetrievalSourceRegistry()
    registry.register("arxiv", _forbidden_builder("arxiv"))
    registry.register("null_catalog", build_null_catalog_source)

    source = build_retrieval_source(_config("null_catalog"), source_registry=registry)
    assert isinstance(source.query_adapter, NullQueryAdapter)
    assert isinstance(source.search_tool, NullSearchTool)

    assert source.search_tool.search("NULL_QUERY(test)") == ()


def test_arxiv_source_does_not_call_null_catalog(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    registry = RetrievalSourceRegistry()
    registry.register("arxiv", _stub_arxiv_builder)
    registry.register("null_catalog", _forbidden_builder("null_catalog"))

    source = build_retrieval_source(_config("arxiv"), source_registry=registry)
    assert isinstance(source.query_adapter, ArxivQueryAdapter)
    source.search_tool.search("all:test")
    assert source.search_tool.queries
    assert all("all:" in query for query in source.search_tool.queries)


def test_null_adapter_validates_references_and_preserves_tracking() -> None:
    plan = SearchPlan(
        task_id="T1",
        novelty_point_id="NP1",
        concepts=[SearchConcept(concept_id="C1", name="one", terms=["term one"])],
        strategies=[SearchStrategy(strategy_id="S1", level="strict", expression="C1")],
    )
    query = NullQueryAdapter().compile(plan)[0]
    assert (query.database, query.task_id, query.novelty_point_id, query.strategy_id, query.level) == (
        "null_catalog", "T1", "NP1", "S1", "strict"
    )
    assert query.query == "NULL_QUERY(CONCEPT[C1:term one])"

    invalid = plan.model_copy(
        update={"strategies": [SearchStrategy(strategy_id="S2", level="broad", expression="C2")]}
    )
    with pytest.raises(ValueError, match="未定义 Concept"):
        NullQueryAdapter().compile(invalid)
