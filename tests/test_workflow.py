"""Coordinator → TaskResearcher fan-out → Validator 主工作流测试。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from novelty_agent_framework.agents import (
    DefaultEvidenceValidator,
    DemoCoordinator,
    DemoPointExtractor,
)
from novelty_agent_framework.ports import ValidationResult
from novelty_agent_framework.schemas import (
    EvidenceCard,
    EvidenceSource,
    NoveltyBrief,
    PaperInput,
    TaskResearchRequest,
    TaskResearchResult,
    TaskResearchStatus,
)
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
        abstract="测试摘要",
        full_text="测试正文",
        claimed_contributions=[f"创新声明 {index}" for index in range(1, claims + 1)],
    )


def make_card(request: TaskResearchRequest) -> EvidenceCard:
    task = request.research_task
    point = request.novelty_point
    return EvidenceCard(
        card_id=f"CARD-{point.point_id}-{task.task_id}",
        task_id=task.task_id,
        novelty_point_id=point.point_id,
        document_title=f"Candidate {point.point_id} {task.task_id}",
        main_contribution="候选贡献",
        overlaps=["技术重合"],
        differences=["范围不同"],
        sources=[
            EvidenceSource(
                title=f"Candidate {point.point_id} {task.task_id}",
                quote="Grounded quote.",
                location="artifact chars:0-15",
                url="https://example.test/paper",
            )
        ],
        relevance=0.9,
        confidence=0.9,
    )


class RecordingTaskResearcher:
    def __init__(self, *, fail_task: str | None = None, first_round_empty=False):
        self.fail_task = fail_task
        self.first_round_empty = first_round_empty
        self.calls: list[TaskResearchRequest] = []
        self.active = 0
        self.max_active = 0

    async def ainvoke(self, request: TaskResearchRequest) -> TaskResearchResult:
        self.calls.append(request)
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        await asyncio.sleep(0.01)
        self.active -= 1
        if request.research_task.task_id == self.fail_task:
            raise RuntimeError("task failed")
        cards = []
        if not (self.first_round_empty and request.research_task.attempt == 1):
            cards = [make_card(request)]
        return TaskResearchResult(
            task_id=request.research_task.task_id,
            novelty_point_id=request.novelty_point.point_id,
            status=TaskResearchStatus.COMPLETED,
            evidence_cards=cards,
            steps_used=1,
        )


class RecordingValidator:
    def __init__(self, researcher: RecordingTaskResearcher):
        self.researcher = researcher
        self.calls: list[tuple[int, int]] = []
        self.delegate = DefaultEvidenceValidator()

    def validate(self, cards, *, tasks):
        self.calls.append((len(cards), len(self.researcher.calls)))
        return self.delegate.validate(cards, tasks=tasks)


def build_workflow(researcher=None, validator=None, **config):
    researcher = researcher or RecordingTaskResearcher()
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            task_researcher=researcher,
            point_extractor=DemoPointExtractor(),
            validator=validator,
        ),
        NoveltyWorkflowConfig(**config),
    ), researcher


def test_graph_replaces_fixed_retrieval_nodes():
    nodes = NoveltyWorkflow.default().graph.get_graph().nodes
    assert "dispatch_research_tasks" in nodes
    assert "run_research_task" in nodes
    assert "validate_evidence" in nodes
    assert "plan_search" not in nodes
    assert "retrieve_candidates" not in nodes
    assert "parallel_research" not in nodes


def test_each_task_is_isolated_and_fan_out_runs_concurrently():
    workflow, researcher = build_workflow(max_concurrency=4)
    result = workflow.run(make_paper(claims=2))
    assert len(researcher.calls) == 4
    assert researcher.max_active > 1
    assert all(
        call.research_task.novelty_point_id == call.novelty_point.point_id
        for call in researcher.calls
    )
    assert len(result.evidence_cards) == 4


def test_validator_runs_once_after_current_round_fan_in():
    researcher = RecordingTaskResearcher()
    validator = RecordingValidator(researcher)
    workflow, _ = build_workflow(researcher, validator, max_rounds=1)
    workflow.run(make_paper())
    assert validator.calls == [(2, 2)]


def test_single_task_failure_does_not_cancel_siblings():
    researcher = RecordingTaskResearcher(fail_task="T-1")
    workflow, _ = build_workflow(researcher, max_rounds=1)
    result = workflow.run(make_paper())
    assert len(researcher.calls) == 2
    assert result.evidence_cards
    assert any(issue.code == "research_task_failed" for issue in result.issues)


def test_supplement_dispatches_only_new_tasks():
    researcher = RecordingTaskResearcher(first_round_empty=True)
    workflow, _ = build_workflow(researcher, max_rounds=2)
    result = workflow.run(make_paper())
    assert result.rounds == 2
    assert [call.research_task.task_id for call in researcher.calls] == [
        "T-1",
        "T-2",
        "T-R2-1",
        "T-R2-2",
    ]
    assert result.evidence_cards


class NoTaskCoordinator(DemoCoordinator):
    def plan(self, paper, *, points, attempt):
        brief = super().plan(paper, points=points, attempt=attempt)
        return brief.model_copy(update={"research_tasks": []})

    def plan_supplement(self, paper, *, brief, existing_evidence, coverage_gaps, attempt):
        return brief.model_copy(update={"research_tasks": []})


def test_no_tasks_branch_does_not_hang():
    researcher = RecordingTaskResearcher()
    workflow = NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=NoTaskCoordinator(),
            task_researcher=researcher,
            point_extractor=DemoPointExtractor(),
        ),
        NoveltyWorkflowConfig(max_rounds=1),
    )
    result = workflow.run(make_paper())
    assert researcher.calls == []
    assert result.coverage_gaps


def test_task_audit_and_compatibility_files_are_written():
    workflow, _ = build_workflow(max_rounds=1)
    workflow.run(make_paper())
    assert Path(
        "outputs/paper-test/research-runs/NP-1/T-1/attempt-1.json"
    ).is_file()
    retrieval = json.loads(
        Path("outputs/paper-test/retrieval-plans.json").read_text(encoding="utf-8")
    )
    assert retrieval["paper_id"] == "paper-test"
    assert Path("outputs/paper-test/evidence-cards.json").is_file()


def test_default_demo_runs_offline():
    result = NoveltyWorkflow.default().run(make_paper())
    assert result.rounds == 1
    assert result.evidence_cards
