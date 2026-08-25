"""任务级 Researcher 子工作流的数据契约。"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints, model_validator

from .domain import EvidenceCard, NoveltyPoint, ResearchTask, StrictModel
from .references import Evidence, ResearchBundle
from .research_tools import ResearchFinishDraft, ReferenceReadResult

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TaskResearchRequest(StrictModel):
    subject_paper_id: NonEmptyStr
    run_id: NonEmptyStr
    novelty_point: NoveltyPoint
    research_task: ResearchTask

    @model_validator(mode="after")
    def bind_task(self) -> TaskResearchRequest:
        if self.research_task.novelty_point_id != self.novelty_point.point_id:
            raise ValueError("research_task must belong to novelty_point")
        return self


class CallToolAction(StrictModel):
    action: Literal["call_tool"]
    tool_name: NonEmptyStr
    arguments: dict[str, Any] = Field(default_factory=dict)


class FinishResearchAction(StrictModel):
    action: Literal["finish"]
    draft: ResearchFinishDraft

    @property
    def cards(self):
        """Read-only bridge for the not-yet-migrated TaskResearcherWorkflow."""

        return self.draft.cards


ResearcherAction = Annotated[
    CallToolAction | FinishResearchAction, Field(discriminator="action")
]


class TaskResearchStatus(StrEnum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class ResearcherToolObservation(StrictModel):
    tool_name: NonEmptyStr
    arguments: dict[str, Any] = Field(default_factory=dict)
    succeeded: bool
    summary: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    elapsed_ms: int = Field(default=0, ge=0)


class TaskResearchResult(StrictModel):
    task_id: NonEmptyStr
    novelty_point_id: NonEmptyStr
    status: TaskResearchStatus
    research_bundles: list[ResearchBundle] = Field(default_factory=list)
    read_results: list[ReferenceReadResult] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    evidence_cards: list[EvidenceCard] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    steps_used: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_bindings(self) -> TaskResearchResult:
        evidence_ids = {item.evidence_id for item in self.evidence}
        for item in self.evidence:
            if item.task_id != self.task_id or item.novelty_point_id != self.novelty_point_id:
                raise ValueError(f"evidence {item.evidence_id} has wrong task binding")
        for card in self.evidence_cards:
            if card.task_id != self.task_id or card.novelty_point_id != self.novelty_point_id:
                raise ValueError(f"evidence card {card.card_id} has wrong task binding")
            missing = set(card.evidence_ids) - evidence_ids
            if missing:
                raise ValueError(f"evidence card {card.card_id} references missing evidence {sorted(missing)}")
        return self
