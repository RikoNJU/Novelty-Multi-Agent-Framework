"""任务级 Researcher 子工作流的数据契约。"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints, model_validator

from .domain import EvidenceCard, NoveltyPoint, ResearchTask, StrictModel
from .references import ArtifactRole, Evidence, ResearchBundle

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


class ReferenceReadRequest(StrictModel):
    subject_paper_id: NonEmptyStr
    artifact_id: NonEmptyStr
    char_start: int = Field(default=0, ge=0)
    max_chars: int = Field(default=8_000, ge=1, le=16_000)


class ReferenceReadResult(StrictModel):
    read_id: NonEmptyStr
    work_id: NonEmptyStr
    artifact_id: NonEmptyStr
    role: ArtifactRole
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    text: str
    has_more: bool
    sha256: NonEmptyStr

    @model_validator(mode="after")
    def valid_range(self) -> ReferenceReadResult:
        if self.char_end < self.char_start:
            raise ValueError("char_end must not be before char_start")
        if self.char_end - self.char_start != len(self.text):
            raise ValueError("read range must match text length")
        return self


class CallToolAction(StrictModel):
    action: Literal["call_tool"]
    tool_name: NonEmptyStr
    arguments: dict[str, Any] = Field(default_factory=dict)


class EvidenceQuoteDraft(StrictModel):
    read_id: NonEmptyStr
    quote: NonEmptyStr
    interpretation: NonEmptyStr
    confidence: float = Field(ge=0.0, le=1.0)


class EvidenceCardDraft(StrictModel):
    work_id: NonEmptyStr
    main_contribution: NonEmptyStr
    overlaps: list[NonEmptyStr] = Field(default_factory=list)
    differences: list[NonEmptyStr] = Field(default_factory=list)
    quotes: list[EvidenceQuoteDraft] = Field(default_factory=list)
    possible_baseline: bool = False
    relevance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class FinishResearchAction(StrictModel):
    action: Literal["finish"]
    cards: list[EvidenceCardDraft] = Field(default_factory=list)


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


class StructuredRetrievalToolArguments(StrictModel):
    source_id: NonEmptyStr


class ReferenceReaderToolArguments(StrictModel):
    artifact_id: NonEmptyStr
    char_start: int = Field(default=0, ge=0)
    max_chars: int = Field(default=8_000, ge=1, le=16_000)
