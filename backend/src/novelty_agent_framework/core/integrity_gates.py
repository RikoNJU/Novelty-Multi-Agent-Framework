"""Deterministic referential-integrity gates for synthesis inputs and reports."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Sequence

from ..persistence import ReferenceStore
from ..schemas import (
    Evidence,
    EvidenceCard,
    NoveltyPoint,
    NoveltyReport,
    ResearchTask,
)
from ..tools.evidence_card_builder import normalize_quote_whitespace


@dataclass(frozen=True)
class SynthesisIntegrityResult:
    accepted: tuple[EvidenceCard, ...]
    rejected: tuple[tuple[EvidenceCard, tuple[str, ...]], ...]

    def audit(self) -> dict[str, Any]:
        return {
            "validation_passed": not self.rejected,
            "checked_card_count": len(self.accepted) + len(self.rejected),
            "accepted_card_count": len(self.accepted),
            "rejected_card_count": len(self.rejected),
            "accepted_card_ids": [card.card_id for card in self.accepted],
            "rejected_card_ids": [card.card_id for card, _ in self.rejected],
            "rejected_cards": [
                {"card_id": card.card_id, "reasons": list(reasons)}
                for card, reasons in self.rejected
            ],
        }


@dataclass(frozen=True)
class ReportIntegrityResult:
    validation_passed: bool
    checked_conclusion_count: int
    referenced_card_count: int
    reference_occurrence_count: int
    issues: tuple[str, ...]

    def audit(self) -> dict[str, Any]:
        return {
            "validation_passed": self.validation_passed,
            "checked_conclusion_count": self.checked_conclusion_count,
            "referenced_card_count": self.referenced_card_count,
            "reference_occurrence_count": self.reference_occurrence_count,
            "issues": list(self.issues),
        }


def validate_synthesis_input(
    cards: Sequence[EvidenceCard],
    *,
    evidence: Sequence[Evidence],
    tasks: Sequence[ResearchTask],
    novelty_points: Sequence[NoveltyPoint],
    paper_id: str,
    reference_store: ReferenceStore,
) -> SynthesisIntegrityResult:
    """Filter cards whose deterministic provenance chain is incomplete."""

    # Loading validates the manifest's own Work/SourceRecord/Artifact relations.
    manifest = reference_store.load_manifest(paper_id)
    works = {item.work_id: item for item in manifest.works}
    artifacts = {item.artifact_id: item for item in manifest.artifacts}
    point_ids = {item.point_id for item in novelty_points}
    task_ids = {task.task_id for task in tasks}
    task_pairs = {(task.task_id, task.novelty_point_id) for task in tasks}
    evidence_candidates: dict[str, list[Evidence]] = {}
    for item in evidence:
        evidence_candidates.setdefault(item.evidence_id, []).append(item)
    card_id_counts = Counter(card.card_id for card in cards)
    verified_files: dict[str, bytes] = {}
    file_errors: dict[str, str] = {}

    accepted: list[EvidenceCard] = []
    rejected: list[tuple[EvidenceCard, tuple[str, ...]]] = []
    for card in cards:
        reasons: list[str] = []
        if card_id_counts[card.card_id] != 1:
            reasons.append(f"duplicate card_id: {card.card_id}")
        if card.task_id not in task_ids:
            reasons.append(f"unknown task_id: {card.task_id}")
        elif (card.task_id, card.novelty_point_id) not in task_pairs:
            reasons.append(
                "card task/novelty-point mismatch: "
                f"{card.task_id} does not belong to {card.novelty_point_id}"
            )
        if card.novelty_point_id not in point_ids:
            reasons.append(f"unknown novelty_point_id: {card.novelty_point_id}")
        if not card.evidence_ids:
            reasons.append("evidence_ids is empty")

        resolved_evidence: list[Evidence] = []
        for evidence_id in card.evidence_ids:
            candidates = evidence_candidates.get(evidence_id, [])
            if not candidates:
                reasons.append(f"missing Evidence: {evidence_id}")
                continue
            distinct = {
                item.model_dump_json(exclude_none=False) for item in candidates
            }
            if len(distinct) > 1:
                reasons.append(f"ambiguous Evidence: {evidence_id}")
                continue
            resolved_evidence.append(candidates[0])

        for item in resolved_evidence:
            reasons.extend(
                _validate_evidence_chain(
                    card,
                    item,
                    works=works,
                    artifacts=artifacts,
                    paper_id=paper_id,
                    reference_store=reference_store,
                    verified_files=verified_files,
                    file_errors=file_errors,
                )
            )

        unique_reasons = tuple(dict.fromkeys(reasons))
        if unique_reasons:
            rejected.append((card, unique_reasons))
        else:
            accepted.append(card)

    return SynthesisIntegrityResult(tuple(accepted), tuple(rejected))


def _validate_evidence_chain(
    card: EvidenceCard,
    evidence: Evidence,
    *,
    works: dict[str, Any],
    artifacts: dict[str, Any],
    paper_id: str,
    reference_store: ReferenceStore,
    verified_files: dict[str, bytes],
    file_errors: dict[str, str],
) -> list[str]:
    reasons: list[str] = []
    if evidence.task_id != card.task_id:
        reasons.append(
            f"cross-task Evidence: {evidence.evidence_id} belongs to "
            f"{evidence.task_id}, not {card.task_id}"
        )
    if evidence.novelty_point_id != card.novelty_point_id:
        reasons.append(
            f"cross-point Evidence: {evidence.evidence_id} belongs to "
            f"{evidence.novelty_point_id}, not {card.novelty_point_id}"
        )
    if evidence.work_id not in works:
        reasons.append(f"missing Work: {evidence.work_id}")
    artifact = artifacts.get(evidence.artifact_id)
    if artifact is None:
        reasons.append(f"missing Artifact: {evidence.artifact_id}")
        return reasons
    if artifact.work_id != evidence.work_id:
        reasons.append(
            f"Artifact/Evidence work mismatch: {artifact.artifact_id} belongs to "
            f"{artifact.work_id}, not {evidence.work_id}"
        )

    if artifact.artifact_id not in verified_files and artifact.artifact_id not in file_errors:
        try:
            _verified, _path, raw = reference_store.verify_artifact_file(
                paper_id, artifact.artifact_id
            )
            verified_files[artifact.artifact_id] = raw
        except (OSError, ValueError) as exc:
            file_errors[artifact.artifact_id] = f"{type(exc).__name__}: {exc}"
    file_error = file_errors.get(artifact.artifact_id)
    if file_error is not None:
        reasons.append(f"invalid Artifact file {artifact.artifact_id}: {file_error}")
        return reasons

    locator = evidence.locator
    if locator is None:
        return reasons
    start, end = locator.char_start, locator.char_end
    if start is None and end is None:
        return reasons
    if start is None or end is None:
        reasons.append(f"incomplete character locator: {evidence.evidence_id}")
        return reasons
    raw = verified_files[artifact.artifact_id]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        reasons.append(f"Artifact is not UTF-8 text: {artifact.artifact_id}")
        return reasons
    if start >= end or end > len(text):
        reasons.append(
            f"invalid character locator: {evidence.evidence_id} "
            f"[{start}, {end}) for length {len(text)}"
        )
        return reasons
    located = text[start:end]
    if normalize_quote_whitespace(located) != normalize_quote_whitespace(
        evidence.quote
    ):
        reasons.append(f"quote/locator mismatch: {evidence.evidence_id}")
    return reasons


def validate_report_integrity(
    report: NoveltyReport,
    *,
    novelty_points: Sequence[NoveltyPoint],
    evidence_cards: Sequence[EvidenceCard],
) -> ReportIntegrityResult:
    """Check report point coverage and references without modifying the report."""

    expected = Counter(point.point_id for point in novelty_points)
    actual = Counter(item.novelty_point_id for item in report.conclusions)
    issues: list[str] = []
    for point_id, count in expected.items():
        if actual[point_id] < count:
            issues.append(f"missing conclusion: {point_id}")
        elif actual[point_id] > count:
            issues.append(f"duplicate conclusion: {point_id}")
    for point_id in actual.keys() - expected.keys():
        issues.append(f"unknown conclusion: {point_id}")

    cards_by_id = {card.card_id: card for card in evidence_cards}
    referenced: list[str] = []
    for conclusion in report.conclusions:
        supporting = conclusion.supporting_card_ids
        counter = conclusion.counter_card_ids
        referenced.extend(supporting)
        referenced.extend(counter)
        for label, card_ids in (("supporting", supporting), ("counter", counter)):
            for card_id, count in Counter(card_ids).items():
                if count > 1:
                    issues.append(
                        f"duplicate {label} card reference: "
                        f"{conclusion.novelty_point_id} -> {card_id}"
                    )
            for card_id in card_ids:
                card = cards_by_id.get(card_id)
                if card is None:
                    issues.append(f"unknown card reference: {card_id}")
                elif card.novelty_point_id != conclusion.novelty_point_id:
                    issues.append(
                        f"cross-point reference: {conclusion.novelty_point_id} -> "
                        f"{card_id} (belongs to {card.novelty_point_id})"
                    )
        for card_id in sorted(set(supporting) & set(counter)):
            issues.append(
                f"supporting/counter conflict: "
                f"{conclusion.novelty_point_id} -> {card_id}"
            )

    unique_issues = tuple(dict.fromkeys(issues))
    return ReportIntegrityResult(
        validation_passed=not unique_issues,
        checked_conclusion_count=len(report.conclusions),
        referenced_card_count=len(set(referenced)),
        reference_occurrence_count=len(referenced),
        issues=unique_issues,
    )


__all__ = [
    "ReportIntegrityResult",
    "SynthesisIntegrityResult",
    "validate_report_integrity",
    "validate_synthesis_input",
]
