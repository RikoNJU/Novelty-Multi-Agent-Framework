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
    ReportNarrativeDraft,
)


def assemble_report_from_draft(
    draft: ReportNarrativeDraft,
    *,
    paper_id: str,
    novelty_reviews: Sequence[NoveltyPointReview],
    novelty_points: Sequence[NoveltyPoint],
    evidence_cards: Sequence[EvidenceCard],
    rejected_evidence: Sequence[str] = (),
) -> NoveltyReport:
    """Assemble a complete report without asking the model to repeat authority fields."""

    point_counts = Counter(point.point_id for point in novelty_points)
    review_counts = Counter(review.novelty_point_id for review in novelty_reviews)
    narrative_counts = Counter(item.novelty_point_id for item in draft.conclusions)
    if any(count != 1 for count in point_counts.values()):
        raise ValueError("novelty_points must contain unique point_id values")
    _require_exact_coverage("review", point_counts, review_counts)
    _require_exact_coverage("conclusion", point_counts, narrative_counts)
    cards_by_id = _unique_cards(evidence_cards)
    reviews_by_id = {item.novelty_point_id: item for item in novelty_reviews}
    narrative_by_id = {item.novelty_point_id: item for item in draft.conclusions}
    conclusions = []
    # Free-form model limitations can imply unrecorded search coverage or causes.
    # Keep the draft in the raw response, but publish only traceable state here.
    limitations: list[str] = []
    for point in novelty_points:
        review = reviews_by_id[point.point_id]
        narrative = narrative_by_id[point.point_id]
        _validate_card_groups(narrative, cards_by_id)
        values = {
            "novelty_point_id": point.point_id,
            "summary": narrative.summary,
            "supporting_card_ids": list(narrative.supporting_card_ids),
            "counter_card_ids": list(narrative.counter_card_ids),
            **_review_fields(review),
        }
        if review.status.value == "insufficient_evidence":
            values["summary"] = _limited_summary(review)
            limitations.append(
                f"{point.point_id}：Reviewer 核验未完成；原因："
                f"{review.incomplete_reason or '未记录'}。"
            )
        if review.supplement_request is not None:
            limitations.append(
                f"{point.point_id}：Reviewer 提出补查请求；原始请求保留在来源 Review，"
                "本报告节点未执行补查。"
            )
        conclusions.append(NoveltyConclusion.model_validate(values))
    for rejected in rejected_evidence:
        limitations.append(
            f"被拒绝证据：{rejected}" if ": " in rejected
            else f"被拒绝证据：{rejected}；来源未提供拒绝原因。"
        )
    limitations.append("本报告节点输入未提供完整检索执行事实，检索覆盖状态未知。")
    return NoveltyReport.model_validate({
        "paper_id": paper_id,
        "conclusions": conclusions,
        "limitations": list(dict.fromkeys(limitations)),
    })


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
        values.update(_review_fields(review))
        if review.status.value == "insufficient_evidence":
            values["summary"] = _limited_summary(review)
        conclusions.append(NoveltyConclusion.model_validate(values))
    values = draft.model_dump(mode="python")
    values["conclusions"] = conclusions
    return NoveltyReport.model_validate(values)


def _review_fields(review: NoveltyPointReview) -> dict:
    return {
        "review_status": review.status,
        "verdict": review.verdict,
        "verdict_reason": review.verdict_reason,
        "confidence": review.confidence,
        "highly_relevant_works": list(review.highly_relevant_works),
        "review_evidence": list(review.review_evidence),
        "feature_comparisons": list(review.feature_comparisons),
        "incomplete_reason": review.incomplete_reason,
    }


def _limited_summary(review: NoveltyPointReview) -> str:
    return (
        "Reviewer 核验未完成，尚不能作出新颖性裁定。"
        if review.incomplete_reason in {"budget_exhausted", "technical_error", "material_unavailable"}
        else "该查新点的关键比较证据不足，尚不能作出新颖性裁定。"
    )


def _unique_cards(evidence_cards: Sequence[EvidenceCard]) -> dict[str, EvidenceCard]:
    counts = Counter(card.card_id for card in evidence_cards)
    duplicate = [card_id for card_id, count in counts.items() if count > 1]
    if duplicate:
        raise ValueError(f"duplicate authorized card: {', '.join(duplicate)}")
    return {card.card_id: card for card in evidence_cards}


def _validate_card_groups(narrative, cards_by_id: dict[str, EvidenceCard]) -> None:
    supporting = narrative.supporting_card_ids
    counter = narrative.counter_card_ids
    if len(set(supporting)) != len(supporting) or len(set(counter)) != len(counter):
        raise ValueError(f"duplicate card reference: {narrative.novelty_point_id}")
    if set(supporting) & set(counter):
        raise ValueError(f"supporting/counter conflict: {narrative.novelty_point_id}")
    for card_id in [*supporting, *counter]:
        card = cards_by_id.get(card_id)
        if card is None:
            raise ValueError(f"unknown card reference: {card_id}")
        if card.novelty_point_id != narrative.novelty_point_id:
            raise ValueError(
                f"cross-point reference: {narrative.novelty_point_id} -> {card_id}"
            )


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
