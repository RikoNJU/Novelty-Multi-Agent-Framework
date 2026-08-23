"""arXiv 与 null_catalog 在同一注入位置竞争，active_source 只有一个赢家。"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest

from novelty_agent_framework.agents import (
    DemoCoordinator,
    DemoPointExtractor,
    DemoResearchAgent,
    DemoSearchPlanner,
)
from novelty_agent_framework.config import build_retrieval_source
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.schemas import PaperInput, SearchConcept, SearchPlan, SearchStrategy
from novelty_agent_framework.tools import (
    ArxivQueryAdapter,
    NullQueryAdapter,
    NullSearchTool,
    RetrievalSource,
    RetrievalSourceRegistry,
)
from novelty_agent_framework.tools.null_catalog import build_null_catalog_source
from novelty_agent_framework.workflows import (
    NoveltyWorkflow,
    NoveltyWorkflowConfig,
    NoveltyWorkflowServices,
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
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            research_agent=DemoResearchAgent(),
            search_planner=DemoSearchPlanner(),
            query_adapter=source.query_adapter,
            point_extractor=DemoPointExtractor(),
            search_tool=source.search_tool,
            full_text_tool=source.full_text_tool,
            metadata_tool=source.metadata_tool,
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

    result = _workflow(source).run(_paper())
    persisted = json.loads(
        Path("outputs/null-source-test/retrieval-plans.json").read_text(encoding="utf-8")
    )
    executed = persisted["novelty_point_plans"][0]["executed_queries"]
    assert executed and {item["database"] for item in executed} == {"null_catalog"}
    assert all(item["query"].startswith("NULL_QUERY(") for item in executed)
    assert result.evidence_cards == []
    assert any(issue.code == "no_candidates" for issue in result.issues)
    # DemoCoordinator 同时创建中文和英文任务；二者均走 Null 查询。
    assert {task["language"] for task in persisted["novelty_point_plans"][0]["research_tasks"]} == {"zh", "en"}


def test_arxiv_source_does_not_call_null_catalog(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    registry = RetrievalSourceRegistry()
    registry.register("arxiv", _stub_arxiv_builder)
    registry.register("null_catalog", _forbidden_builder("null_catalog"))

    source = build_retrieval_source(_config("arxiv"), source_registry=registry)
    assert isinstance(source.query_adapter, ArxivQueryAdapter)
    result = _workflow(source).run(_paper())
    assert result.evidence_cards == []
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
