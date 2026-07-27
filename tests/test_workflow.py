"""论文查新 LangGraph 骨架的行为测试。"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from novelty_agent_framework.agents import DemoCoordinator, DemoResearchAgent
from novelty_agent_framework.ports import FullTextTool, MetadataTool, SearchTool
from novelty_agent_framework.schemas import (
    ConclusionLevel,
    EvidenceCard,
    EvidenceSource,
    PaperInput,
    ResearchTask,
)
from novelty_agent_framework.workflows import (
    NoveltyWorkflow,
    NoveltyWorkflowConfig,
    NoveltyWorkflowServices,
)


def make_paper(claims: int = 2) -> PaperInput:
    return PaperInput(
        paper_id="paper-test",
        title="证据驱动论文查新",
        abstract="测试论文摘要",
        full_text="测试论文正文",
        claimed_contributions=[f"创新声明 {index}" for index in range(1, claims + 1)],
    )


def make_card(task: ResearchTask, *, sources: bool = True) -> EvidenceCard:
    return EvidenceCard(
        card_id=f"CARD-{task.task_id}",
        task_id=task.task_id,
        novelty_point_id=task.novelty_point_id,
        document_title=f"Related Work {task.task_id}",
        main_contribution="候选文献贡献",
        overlaps=["部分技术重合"],
        differences=["适用范围不同"],
        sources=(
            [
                EvidenceSource(
                    title="Related Work",
                    quote="Direct evidence.",
                    location="Section 2",
                    doi=f"10.0000/{task.task_id.lower()}",
                )
            ]
            if sources
            else []
        ),
        cited_by_paper=False,
        relevance=0.9,
        confidence=0.9,
    )


def build_workflow(research_agent: object, **config: int) -> NoveltyWorkflow:
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            research_agent=research_agent,  # type: ignore[arg-type]
        ),
        NoveltyWorkflowConfig(**config),
    )


def test_demo_runs_total_divide_total_flow() -> None:
    result = build_workflow(DemoResearchAgent()).run(make_paper())

    assert result.rounds == 1
    assert len(result.brief.novelty_points) == 2
    assert len(result.evidence_cards) == 2
    assert len(result.report.conclusions) == 2
    assert {item.level for item in result.report.conclusions} == {ConclusionLevel.PARTIAL}
    assert result.coverage_gaps == []


class ConcurrencyResearchAgent:
    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    async def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        *,
        search_tool: SearchTool | None = None,
        full_text_tool: FullTextTool | None = None,
        metadata_tool: MetadataTool | None = None,
    ) -> Sequence[EvidenceCard]:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        await asyncio.sleep(0.03)
        self.active -= 1
        return [make_card(task)]


def test_research_tasks_run_in_parallel() -> None:
    agent = ConcurrencyResearchAgent()
    result = build_workflow(agent, max_concurrency=3).run(make_paper(claims=3))

    assert agent.max_active == 3
    assert len(result.evidence_cards) == 3


class MissingSourceAgent:
    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        **_: object,
    ) -> Sequence[EvidenceCard]:
        return [make_card(task, sources=False)]


def test_evidence_without_source_is_rejected() -> None:
    result = build_workflow(MissingSourceAgent(), max_rounds=1).run(make_paper(claims=1))

    assert result.evidence_cards == []
    assert len(result.rejected_evidence) == 1
    assert "缺少可追溯文献来源" in result.rejected_evidence[0].reason
    assert result.report.conclusions[0].level is ConclusionLevel.INSUFFICIENT


class SupplementResearchAgent:
    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        **_: object,
    ) -> Sequence[EvidenceCard]:
        if task.attempt == 1:
            return []
        return [make_card(task)]


def test_insufficient_evidence_triggers_supplement() -> None:
    result = build_workflow(SupplementResearchAgent(), max_rounds=2).run(
        make_paper(claims=1)
    )

    assert result.rounds == 2
    assert len(result.evidence_cards) == 1
    assert result.coverage_gaps == []


class EmptyResearchAgent:
    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        **_: object,
    ) -> Sequence[EvidenceCard]:
        return []


def test_workflow_stops_at_maximum_rounds() -> None:
    result = build_workflow(EmptyResearchAgent(), max_rounds=2).run(make_paper(claims=1))

    assert result.rounds == 2
    assert result.coverage_gaps
    assert result.report.conclusions[0].level is ConclusionLevel.INSUFFICIENT


class PartiallyFailingAgent:
    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        **_: object,
    ) -> Sequence[EvidenceCard]:
        if task.novelty_point_id == "NP-1":
            raise RuntimeError("模拟文献服务不可用")
        return [make_card(task)]


def test_one_worker_failure_preserves_other_results() -> None:
    result = build_workflow(PartiallyFailingAgent(), max_rounds=1).run(make_paper())

    assert len(result.evidence_cards) == 1
    assert result.evidence_cards[0].novelty_point_id == "NP-2"
    assert any(issue.code == "research_task_failed" for issue in result.issues)
    assert len(result.report.conclusions) == 2


class PartiallyMalformedAgent:
    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        **_: object,
    ) -> Sequence[EvidenceCard]:
        return [make_card(task), {"card_id": "broken"}]  # type: ignore[list-item]


def test_malformed_card_does_not_discard_valid_card_from_same_worker() -> None:
    result = build_workflow(PartiallyMalformedAgent(), max_rounds=1).run(
        make_paper(claims=1)
    )

    assert len(result.evidence_cards) == 1
    assert any(issue.code == "malformed_evidence_card" for issue in result.issues)
