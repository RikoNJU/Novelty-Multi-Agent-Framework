"""Reviewer authoritative fields are deterministically bound into reports."""

from __future__ import annotations

import asyncio

import pytest

from novelty_agent_framework.agents import DemoCoordinator
from novelty_agent_framework.core import bind_reviews_to_report
from novelty_agent_framework.schemas import (
    NoveltyBrief,
    NoveltyConclusion,
    NoveltyPoint,
    NoveltyPointReview,
    NoveltyReport,
    NoveltyVerdict,
    PaperInput,
    RelevantWork,
    ReviewStatus,
)
from novelty_agent_framework.workflows import NoveltyWorkflow, NoveltyWorkflowServices


def _point(point_id: str = "NP-1") -> NoveltyPoint:
    return NoveltyPoint(point_id=point_id, claim="claim")


def _work() -> RelevantWork:
    return RelevantWork(
        work_id="work-1",
        card_ids=["card-1"],
        evidence_ids=["evidence-1"],
        relevance_reason="direct overlap",
    )


def _review(point_id: str = "NP-1") -> NoveltyPointReview:
    return NoveltyPointReview(
        novelty_point_id=point_id,
        status=ReviewStatus.REVIEWED,
        verdict=NoveltyVerdict.NOVEL,
        verdict_reason="authoritative reason",
        confidence=0.83,
        highly_relevant_works=[_work()],
    )


def _drifted_report() -> NoveltyReport:
    return NoveltyReport(
        paper_id="paper-1",
        conclusions=[
            NoveltyConclusion(
                novelty_point_id="NP-1",
                review_status=ReviewStatus.REVIEWED,
                verdict=NoveltyVerdict.NOT_NOVEL,
                verdict_reason="coordinator drift",
                confidence=0.12,
                summary="Coordinator narrative is retained.",
            )
        ],
    )


def test_binding_overwrites_verdict_confidence_reason_and_relevant_works():
    review = _review()
    report = bind_reviews_to_report(
        _drifted_report(),
        novelty_reviews=[review],
        novelty_points=[_point()],
        evidence_cards=[],
    )

    conclusion = report.conclusions[0]
    assert conclusion.summary == "Coordinator narrative is retained."
    assert conclusion.review_status == review.status
    assert conclusion.verdict == review.verdict
    assert conclusion.verdict_reason == review.verdict_reason
    assert conclusion.confidence == review.confidence
    assert conclusion.highly_relevant_works == review.highly_relevant_works


class DriftingCoordinator(DemoCoordinator):
    def synthesize(self, *args, **kwargs):
        report = super().synthesize(*args, **kwargs)
        drifted = report.conclusions[0].model_copy(
            update={
                "verdict": NoveltyVerdict.NOT_NOVEL,
                "verdict_reason": "coordinator drift",
                "confidence": 0.01,
                "highly_relevant_works": [],
            }
        )
        return report.model_copy(update={"conclusions": [drifted]})


def test_workflow_overwrites_fake_coordinator_judgment_drift():
    point = _point()
    review = _review()
    default = NoveltyWorkflow.default()
    workflow = NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DriftingCoordinator(),
            task_researcher=default.services.task_researcher,
            search_planner=default.services.search_planner,
        )
    )
    output = asyncio.run(
        workflow._synthesize_report(
            {
                "paper": PaperInput(
                    paper_id="paper-1", title="Paper", full_text="body"
                ),
                "novelty_points": [point],
                "brief": NoveltyBrief(
                    paper_summary="summary",
                    novelty_points=[point],
                    research_tasks=[],
                ),
                "evidence_cards": [],
                "novelty_reviews": [review],
                "rejected_evidence": [],
                "insufficient_final_evidence_points": [],
            }
        )
    )

    conclusion = output["report"].conclusions[0]
    assert conclusion.verdict is NoveltyVerdict.NOVEL
    assert conclusion.verdict_reason == "authoritative reason"
    assert conclusion.confidence == 0.83
    assert conclusion.highly_relevant_works == [_work()]


def test_binding_preserves_insufficient_evidence_without_verdict():
    review = NoveltyPointReview(
        novelty_point_id="NP-1",
        status=ReviewStatus.INSUFFICIENT_EVIDENCE,
    )
    report = bind_reviews_to_report(
        _drifted_report(),
        novelty_reviews=[review],
        novelty_points=[_point()],
        evidence_cards=[],
    )

    conclusion = report.conclusions[0]
    assert conclusion.review_status is ReviewStatus.INSUFFICIENT_EVIDENCE
    assert conclusion.verdict is None
    assert conclusion.confidence is None


@pytest.mark.parametrize(
    ("reviews", "match"),
    [
        ([], "missing review: NP-1"),
        ([_review(), _review()], "duplicate review: NP-1"),
        ([_review(), _review("NP-99")], "unknown review: NP-99"),
    ],
)
def test_binding_rejects_missing_duplicate_and_unknown_reviews(reviews, match):
    with pytest.raises(ValueError, match=match):
        bind_reviews_to_report(
            _drifted_report(),
            novelty_reviews=reviews,
            novelty_points=[_point()],
            evidence_cards=[],
        )
