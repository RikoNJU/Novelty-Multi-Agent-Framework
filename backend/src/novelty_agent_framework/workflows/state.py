"""LangGraph 状态和运行时依赖。"""

from __future__ import annotations

from dataclasses import dataclass
from operator import add
from typing import Annotated, TypedDict

from ..schemas import (
    EvidenceCard,
    Evidence,
    NoveltyBrief,
    NoveltyPoint,
    NoveltyReport,
    PaperInput,
    RejectedEvidence,
    ResearchTask,
    TaskResearchResult,
    WorkflowIssue,
)
from ..ports import (
    EvidenceValidator,
    NoveltyCoordinator,
    NoveltyPointExtractor,
    TaskResearcher,
)


class NoveltyState(TypedDict, total=False):
    """一次查新任务在图中的共享状态。"""

    paper: PaperInput
    novelty_points: list[NoveltyPoint]
    brief: NoveltyBrief
    research_tasks: list[ResearchTask]
    all_research_tasks: list[ResearchTask]
    run_id: str
    subject_paper_id: str
    current_point: NoveltyPoint
    current_task: ResearchTask
    task_research_results: Annotated[list[TaskResearchResult], add]
    raw_evidence: Annotated[list[Evidence], add]
    raw_evidence_cards: Annotated[list[EvidenceCard], add]
    evidence_cards: list[EvidenceCard]
    rejected_evidence: list[RejectedEvidence]
    coverage_gaps: list[str]
    issues: Annotated[list[WorkflowIssue], add]
    rounds: int
    report: NoveltyReport
    rendered_report_path: str


@dataclass(frozen=True)
class NoveltyWorkflowConfig:
    """只包含工作流级控制参数，不包含具体 Prompt。"""

    max_rounds: int = 2
    max_concurrency: int = 4
    minimum_evidence_per_point: int = 1
    candidate_limit_per_task: int = 8

    def __post_init__(self) -> None:
        if self.max_rounds < 1:
            raise ValueError("max_rounds 必须至少为 1")
        if self.max_concurrency < 1:
            raise ValueError("max_concurrency 必须至少为 1")
        if self.minimum_evidence_per_point < 1:
            raise ValueError("minimum_evidence_per_point 必须至少为 1")
        if self.candidate_limit_per_task < 1:
            raise ValueError("candidate_limit_per_task 必须至少为 1")


@dataclass(frozen=True)
class NoveltyWorkflowServices:
    """主图只依赖全局角色和任务级 Researcher。"""

    coordinator: NoveltyCoordinator
    task_researcher: TaskResearcher
    point_extractor: NoveltyPointExtractor | None = None
    validator: EvidenceValidator | None = None
