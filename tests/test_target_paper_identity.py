from __future__ import annotations

import asyncio
import json

from backend.env import ModelResponse, ModelToolCall

from novelty_agent_framework.core.target_paper_identity import (
    filter_target_observation, match_target, normalize_title,
)
from novelty_agent_framework.schemas import (
    DatabaseSearchArguments, NoveltyPoint, ResearchTask, ResearcherToolObservation,
    TaskResearchRequest, EvidenceCardBuilderResult,
)
from novelty_agent_framework.schemas.research import TargetPaperIdentity
from novelty_agent_framework.schemas.research_tools import ReaderCallArguments
from novelty_agent_framework.tools import ResearcherToolRegistry
from novelty_agent_framework.workflows.candidate_audit import build_candidate_audit
from novelty_agent_framework.workflows.research_task import TaskResearcherWorkflow, TaskResearcherConfig
from novelty_agent_framework.core.tool_call_harness import ToolCallHarnessEvent
from conftest import minimal_search_plan


def identity(**updates):
    return TargetPaperIdentity(title="Streaming Graph Partitioning", **updates)


def test_target_identity_matches_strong_ids_and_normalized_title():
    target = identity(identifiers=[
        {"namespace": "doi", "value": "10.1000/ABC"},
        {"namespace": "arxiv", "value": "2401.01234v2"},
        {"namespace": "pmid", "value": "12345678"},
    ])
    assert match_target(target, {"title": "Unrelated", "identifiers": [
        {"namespace": "doi", "value": "https://doi.org/10.1000/abc"}]}) == "doi"
    assert match_target(target, {"title": "Unrelated", "landing_url":
        "https://arxiv.org/abs/2401.01234v3"}) == "arxiv_id"
    assert match_target(target, {"title": "Unrelated", "landing_url":
        "https://pubmed.ncbi.nlm.nih.gov/12345678/"}) == "pmid"
    assert normalize_title("  STREAMING—Graph: Partitioning!  ") == normalize_title(target.title)
    assert match_target(target, {"title": "STREAMING—Graph: Partitioning!"}) == "normalized_title"


def test_target_identity_needs_title_and_authors_for_fuzzy_match():
    target = identity(authors=["Alice Smith", "Bob Lee"])
    near = "Streaming Graph Partitoning"
    assert match_target(target, {"title": near, "authors": ["Alice Smith"]}) == "similar_title_and_authors"
    assert match_target(target, {"title": near, "authors": ["Carol Jones"]}) is None
    assert match_target(target, {"title": "Different Study", "authors": ["Alice Smith"]}) is None


def _scope():
    return TaskResearchRequest(
        subject_paper_id="subject-1", run_id="run-1",
        novelty_point=NoveltyPoint(point_id="NP-1", claim="claim", technical_features=[]),
        research_task=ResearchTask(task_id="T-1", novelty_point_id="NP-1",
                                   task_type="search", language="en"),
        search_plan=minimal_search_plan("T-1", "NP-1"),
        target_identity=identity(),
    )


class FakeDatabase:
    name = "database_search"
    description = "database"
    args_schema = DatabaseSearchArguments

    def __init__(self):
        self.calls = 0

    async def ainvoke(self, arguments, *, scope):
        self.calls += 1
        record = {"source_record_id": "src-self", "work_id": "work-self",
                  "source_id": "arxiv", "title": "Streaming Graph Partitioning",
                  "authors": ["Alice"], "identifiers": []}
        item = {"source_record_id": "src-self", "work_id": "work-self",
                "title": record["title"], "artifact_ids": ["art-self"]}
        return ResearcherToolObservation(tool_name=self.name, succeeded=True,
            payload={"research_bundle": {"works": [{"work_id": "work-self", "title": record["title"]}],
                         "source_records": [record], "artifacts": [{"artifact_id": "art-self",
                         "work_id": "work-self", "source_record_id": "src-self"}], "evidence": []},
                     "database_search_result": {"source_id": "arxiv", "results": [item], "warnings": []},
                     "source_records": [record], "artifacts": [], "execution_summary": {"no_execution": False}})


class FakeReader:
    name = "reader"
    description = "reader"
    args_schema = ReaderCallArguments

    def __init__(self):
        self.calls = 0

    async def ainvoke(self, arguments, *, scope):
        self.calls += 1
        return ResearcherToolObservation(tool_name=self.name, succeeded=True,
                                         payload={"read_result": {"artifact_id": arguments.artifact_id}})


def test_target_gate_removes_candidate_blocks_reader_and_audits_exclusion():
    reader = FakeReader()
    database = FakeDatabase()
    registry = ResearcherToolRegistry([database, reader])
    scope = _scope()
    found = asyncio.run(registry.execute("database_search", {"source_id": "arxiv"}, scope=scope))
    assert found.payload["database_search_result"]["results"] == []
    assert found.payload["research_bundle"]["source_records"] == []
    assert found.payload["research_bundle"]["artifacts"] == []
    blocked = asyncio.run(registry.execute("reader", {"artifact_id": "art-self"}, scope=scope))
    assert not blocked.succeeded and reader.calls == 0
    fulltext = asyncio.run(registry.execute("database_search", {"source_id": "arxiv",
        "full_text_source_record_ids": ["src-self"]}, scope=scope))
    assert not fulltext.succeeded and database.calls == 1
    trace = [ToolCallHarnessEvent(kind="tool_result", observation=found)]
    audit = build_candidate_audit(trace, [], [], [])
    assert len(audit) == 1
    assert audit[0].status == "excluded" and audit[0].excluded_reason == "target_paper"
    assert audit[0].identity_match == "normalized_title"


def test_unrelated_candidate_is_kept_and_normal_exclude_is_unaffected():
    observation = ResearcherToolObservation(tool_name="reference_search", succeeded=True,
        payload={"reference_search_result": {"results": [
            {"work_id": "other", "title": "Different Study", "authors": ["Alice"],
             "artifact_handles": [{"artifact_id": "other-art"}]},
        ]}})
    filtered, blocked = filter_target_observation(observation, identity(authors=["Alice"]))
    assert not blocked and len(filtered.payload["reference_search_result"]["results"]) == 1


def test_recalled_target_cannot_reach_reader_evidence_or_card():
    class Model:
        def __init__(self):
            self.responses = [
                ModelResponse(content=None, tool_calls=[ModelToolCall(
                    "call-db", "database_search", {"source_id": "arxiv"})]),
                ModelResponse(content=None, tool_calls=[ModelToolCall(
                    "call-read", "reader", {"artifact_id": "art-self"})]),
                ModelResponse(content=json.dumps({"cards": [], "no_evidence_reason":
                                                  "target paper was excluded"})),
            ]

        async def acomplete(self, messages, *, options=None):
            return self.responses.pop(0)

    class Builder:
        def build(self, draft, *, scope, read_results):
            assert not read_results
            return EvidenceCardBuilderResult()

    reader = FakeReader()
    workflow = TaskResearcherWorkflow(Model(), ResearcherToolRegistry([FakeDatabase(), reader]),
                                      Builder(), config=TaskResearcherConfig(max_steps=4))
    result = asyncio.run(workflow.ainvoke(_scope()))
    assert not result.read_results and not result.evidence and not result.evidence_cards
    assert reader.calls == 0
    assert any(row.status == "excluded" for row in result.candidate_audit)
