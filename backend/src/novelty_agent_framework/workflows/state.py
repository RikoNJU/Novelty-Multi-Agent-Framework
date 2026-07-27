"""LangGraph 状态和运行时依赖。"""

from __future__ import annotations

from dataclasses import dataclass
from operator import add
from typing import Annotated, TypedDict

from ..schemas import (
    EvidenceCard,
    NoveltyBrief,
    NoveltyReport,
    PaperInput,
    RejectedEvidence,
    ResearchTask,
    WorkflowIssue,
)
from ..ports import (
    EvidenceValidator,
    FullTextTool,
    LiteratureResearchAgent,
    MetadataTool,
    NoveltyCoordinator,
    SearchTool,
)


class NoveltyState(TypedDict, total=False):
    """一次查新任务在图中的共享状态。"""

    paper: PaperInput
    brief: NoveltyBrief
    research_tasks: list[ResearchTask]
    all_research_tasks: list[ResearchTask]
    raw_evidence_cards: Annotated[list[EvidenceCard], add]
    evidence_cards: list[EvidenceCard]
    rejected_evidence: list[RejectedEvidence]
    coverage_gaps: list[str]
    issues: Annotated[list[WorkflowIssue], add]
    rounds: int
    report: NoveltyReport


@dataclass(frozen=True)
class NoveltyWorkflowConfig:
    """只包含工作流级控制参数，不包含具体 Prompt。"""

    max_rounds: int = 2
    max_concurrency: int = 4
    minimum_evidence_per_point: int = 1

    def __post_init__(self) -> None:
        if self.max_rounds < 1:
            raise ValueError("max_rounds 必须至少为 1")
        if self.max_concurrency < 1:
            raise ValueError("max_concurrency 必须至少为 1")
        if self.minimum_evidence_per_point < 1:
            raise ValueError("minimum_evidence_per_point 必须至少为 1")


@dataclass(frozen=True)
class NoveltyWorkflowServices:
    """注入 Coordinator、Research Agent 和外部工具。"""

    coordinator: NoveltyCoordinator
    research_agent: LiteratureResearchAgent
    validator: EvidenceValidator | None = None
    search_tool: SearchTool | None = None
    full_text_tool: FullTextTool | None = None
    metadata_tool: MetadataTool | None = None
