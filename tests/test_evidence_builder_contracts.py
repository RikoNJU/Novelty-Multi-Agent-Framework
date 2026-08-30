"""Workflow-owned EvidenceCardBuilder contract tests."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from novelty_agent_framework.schemas import (
    BrowserArguments,
    Evidence,
    EvidenceCard,
    EvidenceCardBuilderRequest,
    EvidenceCardBuilderResult,
    EvidenceCardDraft,
    EvidenceLocator,
    EvidenceQuoteDraft,
    ReaderArguments,
    ResearchFinishDraft,
    TaskResearchResult,
    WebSearchArguments,
)


def quote(**updates) -> EvidenceQuoteDraft:
    values = {
        "quote": "Exact source text.",
        "interpretation": "Supports the comparison.",
        "confidence": 0.9,
    }
    values.update(updates)
    return EvidenceQuoteDraft(**values)


def card_draft(**updates) -> EvidenceCardDraft:
    values = {
        "main_contribution": "A contribution",
        "quotes": [quote()],
        "relevance": 0.8,
        "confidence": 0.9,
    }
    values.update(updates)
    return EvidenceCardDraft(**values)


def card(card_id: str, evidence_id: str) -> EvidenceCard:
    return EvidenceCard(
        card_id=card_id,
        task_id="TASK-1",
        novelty_point_id="NP-1",
        document_title="Document",
        main_contribution="Contribution",
        relevance=0.8,
        confidence=0.9,
        evidence_ids=[evidence_id],
    )


def test_semantic_drafts_exclude_all_provenance_handles() -> None:
    assert EvidenceQuoteDraft.model_fields.keys() == {
        "quote", "interpretation", "confidence"
    }
    assert EvidenceCardDraft.model_fields.keys() == {
        "main_contribution",
        "overlaps",
        "differences",
        "quotes",
        "possible_baseline",
        "relevance",
        "confidence",
    }
    finish = ResearchFinishDraft(cards=[card_draft()])
    serialized = json.dumps(finish.model_dump(mode="json"))
    for handle in (
        "read_id", "artifact_id", "work_id", "source_record_id",
        "task_id", "novelty_point_id", "subject_paper_id", "url", "doi",
        "document_title", "card_id", "evidence_id", "locator",
    ):
        assert handle not in serialized


def test_card_requires_quote_and_finish_requires_exactly_one_outcome() -> None:
    with pytest.raises(ValidationError, match="quotes"):
        card_draft(quotes=[])
    with pytest.raises(ValidationError, match="no_evidence_reason"):
        ResearchFinishDraft()
    with pytest.raises(ValidationError, match="must be absent"):
        ResearchFinishDraft(cards=[card_draft()], no_evidence_reason="conflict")
    assert ResearchFinishDraft(cards=[card_draft()]).no_evidence_reason is None
    assert ResearchFinishDraft(
        cards=[], no_evidence_reason="No grounded evidence"
    ).cards == []


def test_locator_is_nullable_but_non_null_contract_remains_strict() -> None:
    evidence = Evidence(
        evidence_id="ev_1",
        work_id="wrk_1",
        artifact_id="art_1",
        quote="Exact source text.",
        interpretation="Supports the comparison.",
        confidence=0.9,
        locator=None,
    )
    assert evidence.locator is None
    assert EvidenceLocator(char_start=0, char_end=10).char_end == 10
    with pytest.raises(ValidationError, match="at least one"):
        EvidenceLocator()


def test_builder_request_result_support_multiple_cards_and_forbid_extra() -> None:
    request = EvidenceCardBuilderRequest(
        draft=ResearchFinishDraft(cards=[card_draft()])
    )
    result = EvidenceCardBuilderResult(
        evidence_cards=[card("card_1", "ev_1"), card("card_2", "ev_2")]
    )
    assert request.draft.cards
    assert len(result.evidence_cards) == 2
    with pytest.raises(ValidationError, match="Extra inputs"):
        EvidenceQuoteDraft(
            quote="text", interpretation="meaning", confidence=0.8,
            read_id="model-must-not-send-this",
        )


def test_existing_three_tool_schemas_are_unchanged() -> None:
    assert WebSearchArguments.model_fields.keys() == {"query", "max_results"}
    assert BrowserArguments.model_fields.keys() == {"source_record_id"}
    assert ReaderArguments.model_fields.keys() == {
        "namespace", "artifact_id", "char_start", "max_chars"
    }


def test_task_result_still_binds_built_evidence_and_cards() -> None:
    evidence = Evidence(
        evidence_id="ev_1",
        work_id="wrk_1",
        artifact_id="art_1",
        novelty_point_id="NP-1",
        task_id="TASK-1",
        quote="Exact source text.",
        interpretation="Supports the comparison.",
        confidence=0.9,
    )
    result = TaskResearchResult(
        task_id="TASK-1",
        novelty_point_id="NP-1",
        status="completed",
        evidence=[evidence],
        evidence_cards=[card("card_1", "ev_1")],
        steps_used=1,
    )
    assert result.evidence_cards[0].evidence_ids == ["ev_1"]
