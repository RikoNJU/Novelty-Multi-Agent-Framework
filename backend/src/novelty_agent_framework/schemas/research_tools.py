"""Data contracts for concrete tools exposed to a Researcher agent."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, TypeAlias

from pydantic import Field, StringConstraints, model_validator

from .domain import EvidenceCard, StrictModel
from .references import ArtifactRole, ContentExtent, Evidence

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class WebSearchArguments(StrictModel):
    """Resource-discovery input; no result produced here is evidence."""

    query: NonEmptyStr
    max_results: int = Field(default=10, ge=1, le=100)


class WebSearchItem(StrictModel):
    source_record_id: NonEmptyStr
    rank: int = Field(ge=1)
    title: NonEmptyStr
    url: NonEmptyStr
    snippet: str | None = None
    score: float | None = None
    published_at: datetime | None = None
    source_name: NonEmptyStr | None = None


class WebSearchResult(StrictModel):
    query: NonEmptyStr
    results: list[WebSearchItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BrowserArguments(StrictModel):
    """Fetch a known source reference; browsing does not judge evidence."""

    source_record_id: NonEmptyStr


class BrowserArtifactItem(StrictModel):
    artifact_id: NonEmptyStr
    role: ArtifactRole
    media_type: NonEmptyStr
    content_extent: ContentExtent


class BrowserResult(StrictModel):
    source_record_id: NonEmptyStr
    work_id: NonEmptyStr
    artifacts: list[BrowserArtifactItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ReaderArguments(StrictModel):
    artifact_id: NonEmptyStr
    char_start: int = Field(default=0, ge=0)
    max_chars: int = Field(default=8_000, ge=1, le=16_000)


class ReferenceReadRequest(StrictModel):
    """Internal deterministic-reader request derived from ReaderArguments."""

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


class EvidenceQuoteDraft(StrictModel):
    """A semantic quote selection without model-supplied provenance handles."""

    quote: NonEmptyStr
    interpretation: NonEmptyStr
    confidence: float = Field(ge=0.0, le=1.0)


class EvidenceCardDraft(StrictModel):
    """One model-authored semantic assessment to be bound by the runtime."""

    main_contribution: NonEmptyStr
    overlaps: list[NonEmptyStr] = Field(default_factory=list)
    differences: list[NonEmptyStr] = Field(default_factory=list)
    quotes: list[EvidenceQuoteDraft] = Field(min_length=1)
    possible_baseline: bool = False
    relevance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class ResearchFinishDraft(StrictModel):
    cards: list[EvidenceCardDraft] = Field(default_factory=list)
    no_evidence_reason: NonEmptyStr | None = None

    @model_validator(mode="after")
    def require_cards_or_reason(self) -> ResearchFinishDraft:
        if self.cards and self.no_evidence_reason is not None:
            raise ValueError("no_evidence_reason must be absent when cards are present")
        if not self.cards and self.no_evidence_reason is None:
            raise ValueError("no_evidence_reason is required when cards are empty")
        return self


class EvidenceCardBuilderRequest(StrictModel):
    draft: ResearchFinishDraft


class EvidenceCardBuilderResult(StrictModel):
    evidence: list[Evidence] = Field(default_factory=list)
    evidence_cards: list[EvidenceCard] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# Deprecated name retained for import compatibility during schema migration.
ReferenceReaderToolArguments: TypeAlias = ReaderArguments
