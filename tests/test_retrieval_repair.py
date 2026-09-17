"""Production control flow regressions with an in-memory async provider."""

from __future__ import annotations

import asyncio
import json

from novelty_agent_framework.agents import DemoQueryAdapter
from novelty_agent_framework.agents.search_plan_compiler import build_fallback_chain
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.core import RuntimeArtifactManager, RuntimeDebugConfig
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.schemas import (
    NoveltyPoint, ResearchTask, SearchConcept, SearchPlan, SearchStrategy,
    StructuredSourceRetrievalRequest, TaskResearchRequest,
)
from novelty_agent_framework.tools.database_search import (
    RetrievalSource, StructuredSourceRetrievalTool,
)
from novelty_agent_framework.tools.database_search.structured_retrieval import ReplayMissError


class Searcher:
    source_id = "demo"

    def __init__(self, counts: list[int]):
        self.counts = counts
        self.calls: list[str] = []

    async def search(self, query: str, *, limit: int = 10):
        index = len(self.calls)
        self.calls.append(query)
        return [SearchHit(document_id=f"p{index}-{rank}", source_id="demo",
                          title=f"Paper {index}-{rank}", abstract="Abstract")
                for rank in range(min(self.counts[index], limit))]


def request() -> StructuredSourceRetrievalRequest:
    plan = SearchPlan(
        task_id="T-1", novelty_point_id="NP-2",
        concepts=[
            SearchConcept(concept_id="C1", name="object", terms=["graph training"], importance=3),
            SearchConcept(concept_id="C2", name="feature", terms=["summary"], importance=3),
        ],
        strategies=[
            SearchStrategy(strategy_id="S1", level="strict", expression="C1 AND C2"),
            SearchStrategy(strategy_id="S2", level="medium", expression="C1 AND C2", use_alias=True),
            SearchStrategy(strategy_id="S3", level="broad", expression="C1"),
        ],
        protected_concept_ids=["C1"],
    )
    return StructuredSourceRetrievalRequest(
        subject_paper_id="repair-paper", source_id="demo", run_id="repair-run",
        novelty_point=NoveltyPoint(point_id="NP-2", claim="claim"),
        research_task=ResearchTask(task_id="T-1", novelty_point_id="NP-2",
                                   task_type="search", language="en"),
        search_plan=plan,
    )


def tool(tmp_path, searcher: Searcher, *, budget: int = 6,
         fallback_protection: bool = True, legacy_candidate_stop: bool = False):
    return StructuredSourceRetrievalTool(
        source=RetrievalSource(source_id="demo", query_adapter=DemoQueryAdapter(),
                               search_tool=searcher),
        reference_store=ReferenceStore(tmp_path), candidate_limit=8,
        per_query_limit=8, max_provider_requests=budget,
        fallback_protection=fallback_protection,
        legacy_candidate_stop=legacy_candidate_stop,
    )


def test_protected_concept_remains_in_fallback():
    chain = build_fallback_chain(request().search_plan)
    assert next(v.expression for v in chain if v.variant_id == "S1-fb1") == "C1"


def test_eight_early_hits_do_not_suppress_other_base_directions(tmp_path):
    searcher = Searcher([8, 1, 1])
    bundle = asyncio.run(tool(tmp_path, searcher).ainvoke(request()))
    executed = [x for x in bundle.search_executions
                if x.status.value in {"succeeded", "partial"}]
    assert [x.parameters["strategy_id"] for x in executed] == ["S1", "S2", "S3"]
    assert len(searcher.calls) == 3
    assert len(bundle.source_records) == 8
    assert any(record.title == "Paper 1-0" for record in bundle.source_records)
    assert any(record.title == "Paper 2-0" for record in bundle.source_records)


def test_budget_marks_unexecuted_base_queries(tmp_path):
    searcher = Searcher([8])
    bundle = asyncio.run(tool(tmp_path, searcher, budget=1).ainvoke(request()))
    not_run = [x for x in bundle.search_executions if x.status.value == "not_run"]
    assert {x.parameters["strategy_id"] for x in not_run} >= {"S2", "S3"}
    assert all(x.parameters["not_run_reason"] == "retrieval_incomplete_budget"
               for x in not_run)


def test_four_control_flow_variants_keep_changes_separate(tmp_path):
    plan = request().search_plan
    def compiled(expression: str) -> str:
        single = plan.model_copy(update={"strategies": [SearchStrategy(
            strategy_id="fixture", level="strict", expression=expression)]})
        return DemoQueryAdapter().compile(single)[0].query

    responses = {
        compiled("C1 AND C2"): [],
        compiled("C1"): [SearchHit(document_id=f"graph-{i}", source_id="demo",
                                   title=f"Graph {i}", abstract="Abstract") for i in range(8)],
        compiled("C2"): [SearchHit(document_id=f"summary-{i}", source_id="demo",
                                   title=f"Summary {i}", abstract="Abstract") for i in range(8)],
    }

    class FixedSearcher(Searcher):
        async def search(self, query: str, *, limit: int = 10):
            self.calls.append(query)
            if query not in responses:
                raise ReplayMissError(query)
            return responses[query][:limit]

    for label, protect, legacy in (
        ("B0", False, True), ("BF", True, True),
        ("BE", False, False), ("BFE", True, False),
    ):
        searcher = FixedSearcher([])
        instance = tool(tmp_path / label, searcher,
                        fallback_protection=protect,
                        legacy_candidate_stop=legacy)
        bundle = asyncio.run(instance.ainvoke(request()))
        executed = [x.parameters["strategy_id"] for x in bundle.search_executions]
        if legacy:
            assert executed == ["S1", "S1-fb1"]
        else:
            assert {"S1", "S2", "S3"} <= set(executed)
        fb = next(x for x in bundle.search_executions
                  if x.parameters["strategy_id"] == "S1-fb1")
        assert (fb.query.endswith("DEMO_CONCEPT(graph training)")) == protect


def test_provider_boundary_and_candidate_selection_are_recorded(tmp_path):
    manager = RuntimeArtifactManager("repair-paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive"),
        run_id="repair-trace")
    searcher = Searcher([8, 1, 1])
    manager.activate()
    source_request = request()
    stage = manager.start_stage("run_research_task", {
        "subject_paper_id": source_request.subject_paper_id,
        "run_id": source_request.run_id,
        "current_point": source_request.novelty_point,
        "current_task": source_request.research_task,
        "current_search_plan": source_request.search_plan,
    })
    bundle = asyncio.run(tool(tmp_path / "store", searcher).ainvoke(source_request))
    manager.finish_stage(stage, {"bundle": bundle})
    manager.deactivate()
    _, archive = manager.finish_run("SUCCESS")
    events = [json.loads(path.read_text()) for path in sorted(
        (archive / "retrieval_events").glob("*.json"))]
    successes = [x for x in events if x.get("status") == "SUCCEEDED"]
    selection = next(x for x in events if x.get("phase") == "candidate_selection")
    assert len(successes) == 3
    assert len(successes[0]["normalized_hits"]) == 8
    assert len(selection["selected_keys"]) == 8
    assert all(x["scope"]["point_id"] == "NP-2" for x in events)
    stage_input = json.loads((archive / "stages" /
                              stage.directory.name / "input.json").read_text())
    reconstructed = TaskResearchRequest(
        subject_paper_id=stage_input["subject_paper_id"],
        run_id=stage_input["run_id"],
        novelty_point=NoveltyPoint.model_validate(stage_input["current_point"]),
        research_task=ResearchTask.model_validate(stage_input["current_task"]),
        search_plan=SearchPlan.model_validate(stage_input["current_search_plan"]),
    )
    assert reconstructed.search_plan.protected_concept_ids == ["C1"]
    assert SearchHit(**successes[0]["normalized_hits"][0]).document_id == "p0-0"


def test_offline_replay_miss_is_not_a_zero_result(tmp_path):
    class MissingSearcher(Searcher):
        async def search(self, query: str, *, limit: int = 10):
            self.calls.append(query)
            raise ReplayMissError(query)

    searcher = MissingSearcher([])
    bundle = asyncio.run(tool(tmp_path, searcher).ainvoke(request()))
    assert bundle.source_records == []
    assert searcher.calls
    assert all(item.status.value == "not_run" and
               item.parameters["not_run_reason"] == "replay_miss"
               for item in bundle.search_executions)
