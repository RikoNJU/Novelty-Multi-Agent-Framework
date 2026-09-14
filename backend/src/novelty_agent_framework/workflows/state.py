"""LangGraph 状态和运行时依赖。"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import add
from typing import Annotated, TypedDict

from ..schemas import (
    EvidenceCard,
    EvidenceReviewDecision,
    Evidence,
    InsufficientFinalEvidence,
    NoveltyBrief,
    NoveltyPoint,
    NoveltyPointReview,
    NoveltyReport,
    PaperInput,
    RejectedEvidence,
    ResearchTask,
    SearchPlan,
    TaskResearchResult,
    WorkflowIssue,
)
from ..ports import (
    EvidenceValidator,
    EvidenceReviewer,
    NoveltyCoordinator,
    NoveltyPointExtractor,
    SearchPlanner,
    TaskResearcher,
)
from ..core.runtime_artifacts import RuntimeDebugConfig
from ..core.retrieval_coverage import RetrievalCoverage


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
    current_search_plan: SearchPlan
    search_plans: Annotated[list[SearchPlan], add]
    task_research_results: Annotated[list[TaskResearchResult], add]
    raw_evidence: Annotated[list[Evidence], add]
    raw_evidence_cards: Annotated[list[EvidenceCard], add]
    validator_accepted_cards: list[EvidenceCard]
    evidence_cards: list[EvidenceCard]
    rejected_evidence: list[RejectedEvidence]
    review_decisions: list[EvidenceReviewDecision]
    novelty_reviews: list[NoveltyPointReview]
    insufficient_final_evidence_points: list[InsufficientFinalEvidence]
    retrieval_coverage: list[RetrievalCoverage]
    subject_reference_resolution: dict
    issues: Annotated[list[WorkflowIssue], add]
    rounds: int
    report: NoveltyReport
    synthesis_integrity: dict
    integrity_rejected_card_ids: Annotated[list[str], add]
    report_integrity: dict
    rendered_report_path: str


@dataclass(frozen=True)
class NoveltyWorkflowConfig:
    """只包含工作流级控制参数，不包含具体 Prompt。"""

    max_rounds: int = 2
    max_concurrency: int = 4
    min_final_evidence_cards_per_point: int = 1
    candidate_limit_per_task: int = 8
    #: 每个查新点最多联网解析多少篇候选参考文献（0 表示不预筛、解析全部）。
    reference_prefilter_limit: int = 4
    # 启用的调研任务语言。关闭的语言不再进入 SearchPlanner 与 Researcher；
    # 任务生成、Prompt 与工具代码全部保留，随时可通过配置恢复。
    enabled_task_languages: tuple[str, ...] = ("zh", "en")
    runtime_debug: RuntimeDebugConfig = field(default_factory=RuntimeDebugConfig)

    def __post_init__(self) -> None:
        if self.max_rounds < 1:
            raise ValueError("max_rounds 必须至少为 1")
        if self.max_concurrency < 1:
            raise ValueError("max_concurrency 必须至少为 1")
        if self.min_final_evidence_cards_per_point < 1:
            raise ValueError("min_final_evidence_cards_per_point 必须至少为 1")
        if self.candidate_limit_per_task < 1:
            raise ValueError("candidate_limit_per_task 必须至少为 1")
        if self.reference_prefilter_limit < 0:
            raise ValueError("reference_prefilter_limit 不能为负")
        if not self.enabled_task_languages:
            raise ValueError("enabled_task_languages 不能为空")
        if any(not str(code).strip() for code in self.enabled_task_languages):
            raise ValueError("enabled_task_languages 不能包含空语言代码")


@dataclass(frozen=True)
class NoveltyWorkflowServices:
    """主图只依赖全局角色和任务级 Researcher。"""

    coordinator: NoveltyCoordinator
    task_researcher: TaskResearcher
    search_planner: SearchPlanner
    point_extractor: NoveltyPointExtractor | None = None
    validator: EvidenceValidator | None = None
    reviewer: EvidenceReviewer | None = None
