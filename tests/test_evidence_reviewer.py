"""Evidence Reviewer 迁移后的输出过滤与 fail 策略契约。"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from backend.env import ModelResponse
from novelty_agent_framework.agents import EvidenceReviewerConfig, NoveltyEvidenceReviewer
from novelty_agent_framework.schemas import EvidenceCard, EvidenceReviewDecision, EvidenceSource


def _card() -> EvidenceCard:
    return EvidenceCard(
        card_id="C1",
        task_id="T1",
        novelty_point_id="NP1",
        document_title="Paper",
        main_contribution="Contribution",
        overlaps=["overlap"],
        differences=["difference"],
        sources=[EvidenceSource(title="Paper", quote="quote")],
        relevance=0.9,
        confidence=0.8,
    )


class StubClient:
    def __init__(self, payload=None, error: Exception | None = None):
        self.payload = payload
        self.error = error

    def complete(self, messages, *, options=None):
        if self.error:
            raise self.error
        return ModelResponse(content=json.dumps(self.payload))


def _review(payload, *, fail_closed=True):
    return NoveltyEvidenceReviewer(
        StubClient(payload),
        config=EvidenceReviewerConfig(fail_closed=fail_closed),
    ).review([_card()], points=[], tasks=[])


def _decision(verdict="accept", *, code=None, card_id="C1", **extra):
    issue = [] if code is None else [{"code": code, "message": "problem", "severity": "warning", "field": "main_contribution", "source_index": 0}]
    return {"card_id": card_id, "verdict": verdict, "issues": issue, "reviewed_confidence": 0.7, **extra}


def test_accept_returns_the_original_card_without_modification():
    card = _card()
    result = NoveltyEvidenceReviewer(StubClient({"decisions": [_decision()]})).review(
        [card], points=[], tasks=[]
    )
    assert result.accepted == (card,)
    assert result.accepted[0] is card


@pytest.mark.parametrize(
    "code",
    [
        "unsupported_main_contribution",
        "unsupported_overlap",
        "unsupported_difference",
        "quote_not_supporting_claim",
        "abstract_only_overclaim",
    ],
)
def test_supported_review_issue_codes_are_preserved(code):
    result = _review({"decisions": [_decision("reject", code=code)]})
    assert result.rejected[0][0] == "C1"
    assert result.decisions[0].issues[0].code == code


def test_unknown_card_id_and_extra_fields_are_filtered():
    unknown = _review({"decisions": [_decision(card_id="hallucinated")]})
    extra = _review({"decisions": [_decision(modified_card={"confidence": 1.0})]})
    assert unknown.rejected == (("C1", "review_missing_decision"),)
    assert extra.rejected == (("C1", "review_missing_decision"),)


def test_decision_schema_rejects_extra_fields():
    with pytest.raises(ValidationError):
        EvidenceReviewDecision.model_validate(_decision(changed_card={}))


def test_needs_more_and_fail_modes_are_unchanged():
    more = _review({"decisions": [_decision("needs_more_evidence")]})
    assert more.needs_more == ("C1",)
    failed_closed = NoveltyEvidenceReviewer(
        StubClient(error=RuntimeError("boom")),
        config=EvidenceReviewerConfig(fail_closed=True),
    ).review([_card()], points=[], tasks=[])
    failed_open = NoveltyEvidenceReviewer(
        StubClient(error=RuntimeError("boom")),
        config=EvidenceReviewerConfig(fail_closed=False),
    ).review([_card()], points=[], tasks=[])
    assert failed_closed.rejected[0][0] == "C1"
    assert failed_open.accepted == (_card(),)
