"""Deterministic Reviewer-to-report authority binding."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from ..schemas import (
    EvidenceCard,
    NoveltyConclusion,
    NoveltyPoint,
    NoveltyPointReview,
    NoveltyReport,
)


def bind_reviews_to_report(
    draft: NoveltyReport,
    *,
    novelty_reviews: Sequence[NoveltyPointReview],
    novelty_points: Sequence[NoveltyPoint],
    evidence_cards: Sequence[EvidenceCard],
) -> NoveltyReport:
    """Replace every report judgment field with the corresponding Reviewer value."""

    del evidence_cards  # Reserved for deterministic card-binding checks.
    point_counts = Counter(point.point_id for point in novelty_points)
    if any(count != 1 for count in point_counts.values()):
        raise ValueError("novelty_points must contain unique point_id values")
    review_counts = Counter(review.novelty_point_id for review in novelty_reviews)
    conclusion_counts = Counter(
        conclusion.novelty_point_id for conclusion in draft.conclusions
    )
    _require_exact_coverage("review", point_counts, review_counts)
    _require_exact_coverage("conclusion", point_counts, conclusion_counts)

    reviews_by_id = {
        review.novelty_point_id: review for review in novelty_reviews
    }
    conclusions_by_id = {
        conclusion.novelty_point_id: conclusion for conclusion in draft.conclusions
    }
    conclusions = []
    for point in novelty_points:
        review = reviews_by_id[point.point_id]
        conclusion = conclusions_by_id[point.point_id]
        values = conclusion.model_dump(mode="python")
        values.update(
            review_status=review.status,
            verdict=review.verdict,
            verdict_reason=review.verdict_reason,
            confidence=review.confidence,
            highly_relevant_works=list(review.highly_relevant_works),
        )
        conclusions.append(NoveltyConclusion.model_validate(values))
    values = draft.model_dump(mode="python")
    values["conclusions"] = conclusions
    return NoveltyReport.model_validate(values)


def _require_exact_coverage(
    label: str,
    expected: Counter[str],
    actual: Counter[str],
) -> None:
    problems = []
    for point_id in expected:
        if actual[point_id] == 0:
            problems.append(f"missing {label}: {point_id}")
        elif actual[point_id] > 1:
            problems.append(f"duplicate {label}: {point_id}")
    for point_id in actual.keys() - expected.keys():
        problems.append(f"unknown {label}: {point_id}")
    if problems:
        raise ValueError("; ".join(problems))
