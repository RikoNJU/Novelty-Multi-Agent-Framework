"""SearchPlanner → Adapter → SearchTool → Researcher 工作流测试。"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

import pytest

from novelty_agent_framework.agents import DemoCoordinator, DemoPointExtractor
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.schemas import (
    ConclusionLevel,
    EvidenceCard,
    EvidenceSource,
    NoveltyPoint,
    PaperInput,
    ResearchTask,
    SearchConcept,
    SearchPlan,
    SearchStrategy,
)
from novelty_agent_framework.tools import ArxivQueryAdapter
from novelty_agent_framework.workflows import (
    NoveltyWorkflow,
    NoveltyWorkflowConfig,
    NoveltyWorkflowServices,
)


@pytest.fixture(autouse=True)
def _isolated_outputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def make_paper(claims: int = 1) -> PaperInput:
    return PaperInput(
        paper_id="paper-test",
        title="证据驱动论文查新",
        abstract="测试论文摘要",
        full_text="测试论文正文",
        claimed_contributions=[f"创新声明 {index}" for index in range(1, claims + 1)],
    )


class RecordingPlanner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def plan(self, point: NoveltyPoint, task: ResearchTask) -> SearchPlan:
        self.calls.append((point.point_id, task.task_id))
        suffix = f"{point.point_id} {task.language}"
        return SearchPlan(
            task_id=task.task_id,
            novelty_point_id=point.point_id,
            concepts=[
                SearchConcept(concept_id="C1", name="core", terms=[f"strict {suffix}"]),
                SearchConcept(concept_id="C2", name="extension", terms=[f"broad {suffix}"]),
            ],
            strategies=[
                SearchStrategy(strategy_id="S1", level="strict", expression="C1"),
                SearchStrategy(
                    strategy_id="S2", level="medium", expression="C1 OR C2"
                ),
                SearchStrategy(strategy_id="S3", level="broad", expression="C2"),
            ],
        )


class RecordingSearchTool:
    def __init__(self, *, enough_immediately: bool = False) -> None:
        self.enough_immediately = enough_immediately
        self.queries: list[tuple[str, int]] = []

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]:
        self.queries.append((query, limit))
        digest = hashlib.sha256(query.encode()).hexdigest()[:10]
        count = limit if self.enough_immediately else 1
        return [
            SearchHit(
                document_id=f"{digest}-{index}",
                title=f"Candidate {digest}-{index}",
                abstract=f"Direct evidence {digest}-{index}.",
                url=f"https://example.test/{digest}-{index}",
            )
            for index in range(count)
        ]


class ProgressiveSearchTool(RecordingSearchTool):
    """逐档返回重复结果和一个新结果，用于验证合并去重。"""

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]:
        self.queries.append((query, limit))
        task_group = "zh" if " zh" in query else "en"
        strategy_index = (len(self.queries) - 1) % 3
        return [
            SearchHit(
                document_id=f"{task_group}-{index}",
                title=f"Candidate {task_group}-{index}",
                abstract=f"Direct evidence {task_group}-{index}.",
                url=f"https://example.test/{task_group}-{index}",
            )
            for index in range(strategy_index + 1)
        ]


class RecordingResearcher:
    def __init__(self, *, first_round_empty: bool = False) -> None:
        self.first_round_empty = first_round_empty
        self.calls: list[tuple[ResearchTask, NoveltyPoint, list[SearchHit]]] = []

    async def research(
        self,
        task: ResearchTask,
        point: NoveltyPoint,
        candidates: Sequence[SearchHit],
        **_: object,
    ) -> Sequence[EvidenceCard]:
        candidates = list(candidates)
        self.calls.append((task, point, candidates))
        if not candidates or (self.first_round_empty and task.attempt == 1):
            return []
        candidate = candidates[0]
        return [
            EvidenceCard(
                card_id=f"CARD-{point.point_id}-{task.task_id}",
                task_id=task.task_id,
                novelty_point_id=point.point_id,
                document_title=candidate.title,
                main_contribution="候选文献贡献",
                overlaps=["部分技术重合"],
                differences=["适用范围不同"],
                sources=[
                    EvidenceSource(
                        title=candidate.title,
                        quote=candidate.abstract,
                        location="abstract",
                        url=candidate.url,
                    )
                ],
                relevance=0.9,
                confidence=0.9,
            )
        ]


def build_workflow(
    *,
    planner: RecordingPlanner | None = None,
    search_tool: RecordingSearchTool | None = None,
    researcher: RecordingResearcher | None = None,
    **config: int,
) -> tuple[NoveltyWorkflow, RecordingPlanner, RecordingResearcher]:
    planner = planner or RecordingPlanner()
    researcher = researcher or RecordingResearcher()
    workflow = NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            research_agent=researcher,
            search_planner=planner,
            query_adapter=ArxivQueryAdapter(),
            point_extractor=DemoPointExtractor(),
            search_tool=search_tool,
        ),
        NoveltyWorkflowConfig(**config),
    )
    return workflow, planner, researcher


def test_complete_chain_uses_composite_task_identity_and_persists_queries() -> None:
    search = RecordingSearchTool(enough_immediately=True)
    workflow, planner, researcher = build_workflow(
        search_tool=search, candidate_limit_per_task=2
    )

    result = workflow.run(make_paper(claims=2))

    assert planner.calls == [
        ("NP-1", "T-1"),
        ("NP-1", "T-2"),
        ("NP-2", "T-1"),
        ("NP-2", "T-2"),
    ]
    assert len(search.queries) == 4
    assert all(query.startswith('all:"strict') for query, _ in search.queries)
    assert all("C1" not in query for query, _ in search.queries)
    assert all(task.novelty_point_id == point.point_id for task, point, _ in researcher.calls)
    assert len(result.evidence_cards) == 4
    assert {card.novelty_point_id for card in result.evidence_cards} == {"NP-1", "NP-2"}

    persisted = json.loads(
        Path("outputs/paper-test/retrieval-plans.json").read_text(encoding="utf-8")
    )
    point_plan = persisted["novelty_point_plans"][0]
    assert point_plan["research_tasks"]
    assert point_plan["search_plans"]
    assert point_plan["executed_queries"]
    assert point_plan["query_plan"]["queries"] == [
        item["query"] for item in point_plan["executed_queries"]
    ]


def test_strict_query_stops_medium_and_broad() -> None:
    search = RecordingSearchTool(enough_immediately=True)
    workflow, _, _ = build_workflow(
        search_tool=search, candidate_limit_per_task=3
    )
    workflow.run(make_paper())
    assert len(search.queries) == 2  # 一个 Point 的中英文两个 Task，各只执行 strict。
    assert all('all:"strict' in query for query, _ in search.queries)


def test_insufficient_strict_query_relaxes_in_strategy_order_and_deduplicates() -> None:
    search = ProgressiveSearchTool()
    workflow, _, researcher = build_workflow(
        search_tool=search, candidate_limit_per_task=3
    )
    workflow.run(make_paper())

    assert len(search.queries) == 6
    for offset in (0, 3):
        queries = [item[0] for item in search.queries[offset : offset + 3]]
        assert "strict" in queries[0]
        assert "strict" in queries[1] and "broad" in queries[1]
        assert "broad" in queries[2]
    assert all(len(candidates) == 3 for _, _, candidates in researcher.calls)


def test_supplement_reenters_entire_retrieval_chain() -> None:
    search = RecordingSearchTool(enough_immediately=True)
    researcher = RecordingResearcher(first_round_empty=True)
    workflow, planner, _ = build_workflow(
        search_tool=search,
        researcher=researcher,
        max_rounds=2,
        candidate_limit_per_task=1,
    )

    result = workflow.run(make_paper())

    assert result.rounds == 2
    assert [task_id for _, task_id in planner.calls] == [
        "T-1",
        "T-2",
        "T-R2-1",
        "T-R2-2",
    ]
    assert [call[0].task_id for call in researcher.calls] == [
        "T-1",
        "T-2",
        "T-R2-1",
        "T-R2-2",
    ]
    assert len(search.queries) == 4
    assert result.coverage_gaps == []


def test_missing_search_tool_does_not_supplement_or_fabricate_evidence() -> None:
    workflow, planner, researcher = build_workflow(search_tool=None, max_rounds=2)
    result = workflow.run(make_paper())

    assert result.rounds == 1
    assert len(planner.calls) == 2
    assert all(not candidates for _, _, candidates in researcher.calls)
    assert result.evidence_cards == []
    assert result.coverage_gaps
    assert result.report.conclusions[0].level is ConclusionLevel.INSUFFICIENT
    assert any(issue.code == "search_tool_unavailable" for issue in result.issues)


def test_default_demo_runs_complete_chain_without_network() -> None:
    result = NoveltyWorkflow.default().run(make_paper())
    assert result.rounds == 1
    assert result.evidence_cards
    assert result.report.conclusions[0].level is ConclusionLevel.PARTIAL
