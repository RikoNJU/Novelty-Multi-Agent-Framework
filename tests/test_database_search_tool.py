from __future__ import annotations

import asyncio
import json

import pytest
from pydantic import ValidationError

from novelty_agent_framework.agents import DemoQueryAdapter
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.ports import FullText, SearchHit
from novelty_agent_framework.schemas import (
    DatabaseSearchArguments,
    NoveltyPoint,
    ResearchTask,
    SearchConcept,
    SearchPlan,
    SearchStrategy,
    TaskResearchRequest,
)
from novelty_agent_framework.tools.database_search import (
    DatabaseSearchTool,
    RetrievalSource,
    StructuredSourceRetrievalTool,
)


class Planner:
    def __init__(self) -> None:
        self.calls = []

    def plan(self, point, task):
        self.calls.append((point, task))
        return SearchPlan(
            task_id=task.task_id,
            novelty_point_id=point.point_id,
            concepts=[SearchConcept(concept_id="C1", name="graph", terms=["graph"])],
            strategies=[SearchStrategy(strategy_id="S1", level="strict", expression="C1")],
        )


class Searcher:
    source_id = "demo"

    def search(self, query, *, limit=10):
        return [
            SearchHit(
                document_id="paper-1",
                external_id="paper-1v2",
                source_id="demo",
                title="Structured Candidate",
                abstract="A database abstract with auditable raw metadata.",
                authors=("Alice", "Bob"),
                year=2025,
                url="https://example.test/paper-1",
                raw_metadata={"private_provider_field": "audit-only"},
            )
        ]


class FullTexts:
    source_id = "demo"

    def fetch(self, document_id):
        return FullText(
            document_id=document_id,
            title="Structured Candidate",
            text="Trusted database artifact text.",
            content_extent="full",
            source_url="https://example.test/paper-1.txt",
        )


def scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id="subject-1",
        run_id="run-1",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="graph novelty", technical_features=["graph"]
        ),
        research_task=ResearchTask(
            task_id="T-1", novelty_point_id="NP-1", task_type="search", language="en"
        ),
    )


def build_tool(tmp_path):
    store = ReferenceStore(tmp_path)
    planner = Planner()
    internal = StructuredSourceRetrievalTool(
        search_planner=planner,
        source=RetrievalSource(
            source_id="demo",
            query_adapter=DemoQueryAdapter(),
            search_tool=Searcher(),
            full_text_tool=FullTexts(),
        ),
        reference_store=store,
        candidate_limit=2,
    )
    return DatabaseSearchTool({"demo": internal}, store), store, planner


def test_arguments_only_accept_and_normalize_source_id():
    assert DatabaseSearchArguments(source_id=" DeMo ").source_id == "demo"
    with pytest.raises(ValidationError):
        DatabaseSearchArguments(source_id="demo", query="untrusted")


def test_unknown_source_fails_clearly(tmp_path):
    tool, _, planner = build_tool(tmp_path)
    with pytest.raises(ValueError, match="unavailable"):
        asyncio.run(tool.ainvoke(DatabaseSearchArguments(source_id="other"), scope=scope()))
    assert planner.calls == []


def test_scope_planning_persistence_projection_and_deduplication(tmp_path):
    tool, store, planner = build_tool(tmp_path)
    observation = asyncio.run(
        tool.ainvoke(DatabaseSearchArguments(source_id="demo"), scope=scope())
    )
    second = asyncio.run(
        tool.ainvoke(DatabaseSearchArguments(source_id="demo"), scope=scope())
    )

    assert planner.calls == [
        (scope().novelty_point, scope().research_task),
        (scope().novelty_point, scope().research_task),
    ]
    assert observation.succeeded and observation.tool_name == "database_search"
    assert "bundle" not in observation.payload
    assert "search_executions" in observation.payload
    assert observation.payload["source_records"][0]["raw_metadata"]
    result = observation.payload["database_search_result"]
    assert len(result["results"]) == 1
    assert result["results"][0]["artifact_ids"]

    manifest = store.load_manifest(scope().subject_paper_id)
    assert len(manifest.works) == 1
    assert len(manifest.source_records) == 1
    assert len(manifest.artifacts) == 2
    assert second.payload["database_search_result"]["results"][0]["work_id"] == manifest.works[0].work_id

    projected = tool.project_model_context(observation)
    serialized = json.dumps(projected)
    assert projected["source_id"] == "demo"
    assert "relative_path" not in serialized
    assert "raw_metadata" not in serialized
    assert "ResearchBundle" not in serialized and "bundle" not in serialized
    assert "private_provider_field" not in serialized


def test_constructor_requires_one_shared_store(tmp_path):
    tool, store, _ = build_tool(tmp_path)
    internal = tool.tools_by_source["demo"]
    with pytest.raises(ValueError, match="share reference_store"):
        DatabaseSearchTool({"demo": internal}, ReferenceStore(tmp_path / "other"))
