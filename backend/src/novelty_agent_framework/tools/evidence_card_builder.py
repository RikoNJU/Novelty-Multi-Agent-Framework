"""Deterministic workflow-owned compiler from semantic drafts to evidence."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence

from ..persistence import ReferenceStore
from ..schemas import (
    Artifact,
    Evidence,
    EvidenceCard,
    EvidenceCardBuilderResult,
    EvidenceCardDraft,
    EvidenceQuoteDraft,
    EvidenceLocator,
    EvidenceSource,
    ReferenceReadResult,
    ResearchFinishDraft,
    SourceRecord,
    TaskResearchRequest,
    Work,
)


class EvidenceCardBuilder:
    """Bind model-authored semantics to trusted persisted provenance."""

    def __init__(self, reference_store: ReferenceStore) -> None:
        self.reference_store = reference_store

    def build(
        self,
        draft: ResearchFinishDraft,
        *,
        scope: TaskResearchRequest,
        read_results: Sequence[ReferenceReadResult],
    ) -> EvidenceCardBuilderResult:
        draft = ResearchFinishDraft.model_validate(draft)
        scope = TaskResearchRequest.model_validate(scope)
        reads = [ReferenceReadResult.model_validate(item) for item in read_results]
        if not draft.cards:
            return EvidenceCardBuilderResult(
                warnings=[f"no evidence: {draft.no_evidence_reason}"]
            )

        manifest = self.reference_store.load_manifest(scope.subject_paper_id)
        works = {item.work_id: item for item in manifest.works}
        artifacts = {item.artifact_id: item for item in manifest.artifacts}
        records = {item.source_record_id: item for item in manifest.source_records}
        all_evidence: list[Evidence] = []
        cards: list[EvidenceCard] = []
        warnings: list[str] = []
        resolved_works: set[str] = set()

        for card_draft in draft.cards:
            matched_by_quote = [
                self._matching_reads(quote, reads, artifacts, records)
                for quote in card_draft.quotes
            ]
            candidate_sets = [
                {read.work_id for read, _artifact in matches}
                for matches in matched_by_quote
            ]
            resolved = set.intersection(*candidate_sets)
            if not resolved:
                raise ValueError("cross-work or inconsistent quote provenance")
            if len(resolved) > 1:
                raise ValueError("ambiguous quote provenance")
            work_id = next(iter(resolved))
            if work_id in resolved_works:
                raise ValueError(f"duplicate evidence card for work {work_id}")
            resolved_works.add(work_id)
            work = works.get(work_id)
            if work is None:
                raise ValueError(f"missing Work {work_id}")

            evidence, sources = self._build_card_items(
                card_draft,
                matched_by_quote,
                work,
                artifacts,
                records,
                scope,
                warnings,
            )
            card = EvidenceCard(
                card_id=_stable_id(
                    "card",
                    scope.subject_paper_id,
                    scope.novelty_point.point_id,
                    scope.research_task.task_id,
                    work_id,
                ),
                task_id=scope.research_task.task_id,
                novelty_point_id=scope.novelty_point.point_id,
                document_title=work.title,
                main_contribution=card_draft.main_contribution,
                overlaps=card_draft.overlaps,
                differences=card_draft.differences,
                sources=sources,
                cited_by_paper=None,
                possible_baseline=card_draft.possible_baseline,
                relevance=card_draft.relevance,
                confidence=card_draft.confidence,
                evidence_ids=[item.evidence_id for item in evidence],
            )
            all_evidence.extend(evidence)
            cards.append(card)

        return EvidenceCardBuilderResult(
            evidence=all_evidence,
            evidence_cards=cards,
            warnings=list(dict.fromkeys(warnings)),
        )

    @staticmethod
    def _matching_reads(
        quote: EvidenceQuoteDraft,
        reads: Sequence[ReferenceReadResult],
        artifacts: dict[str, Artifact],
        records: dict[str, SourceRecord],
    ) -> list[tuple[ReferenceReadResult, Artifact]]:
        matches: list[tuple[ReferenceReadResult, Artifact]] = []
        for read in reads:
            if not _quote_matches(quote.quote, read.text):
                continue
            artifact = artifacts.get(read.artifact_id)
            if artifact is None:
                raise ValueError(f"missing Artifact {read.artifact_id}")
            if artifact.work_id != read.work_id:
                raise ValueError(
                    f"Artifact.work_id mismatch for {read.artifact_id}"
                )
            if (
                artifact.source_record_id is not None
                and artifact.source_record_id not in records
            ):
                raise ValueError(
                    f"Artifact {artifact.artifact_id} references missing SourceRecord"
                )
            matches.append((read, artifact))
        if not matches:
            raise ValueError(f"ungrounded quote: {quote.quote!r}")
        return matches

    @staticmethod
    def _build_card_items(
        draft: EvidenceCardDraft,
        matched_by_quote: Sequence[list[tuple[ReferenceReadResult, Artifact]]],
        work: Work,
        artifacts: dict[str, Artifact],
        records: dict[str, SourceRecord],
        scope: TaskResearchRequest,
        warnings: list[str],
    ) -> tuple[list[Evidence], list[EvidenceSource]]:
        evidence: list[Evidence] = []
        sources: list[EvidenceSource] = []
        for quote, matches in zip(draft.quotes, matched_by_quote, strict=True):
            read, artifact = min(
                (
                    item for item in matches if item[0].work_id == work.work_id
                ),
                key=lambda item: (
                    item[0].artifact_id,
                    item[0].char_start,
                    item[0].char_end,
                    item[0].read_id,
                ),
            )
            # Re-resolve rather than trusting the tuple retained during matching.
            persisted_artifact = artifacts.get(read.artifact_id)
            if persisted_artifact is None:
                raise ValueError(f"missing Artifact {read.artifact_id}")
            if persisted_artifact.work_id != work.work_id:
                raise ValueError(
                    f"Artifact.work_id mismatch for {read.artifact_id}"
                )
            record = _resolve_source_record(persisted_artifact, work, records)
            if record is None:
                warnings.append(f"missing source record for work {work.work_id}")
            local_start, local_end = _find_quote_span(quote.quote, read.text)
            quote_char_start = read.char_start + local_start
            quote_char_end = read.char_start + local_end
            normalized_quote = _normalize_whitespace(quote.quote)
            item = Evidence(
                evidence_id=_stable_id(
                    "ev",
                    scope.subject_paper_id,
                    scope.novelty_point.point_id,
                    scope.research_task.task_id,
                    work.work_id,
                    persisted_artifact.artifact_id,
                    normalized_quote,
                ),
                work_id=work.work_id,
                artifact_id=persisted_artifact.artifact_id,
                novelty_point_id=scope.novelty_point.point_id,
                task_id=scope.research_task.task_id,
                quote=quote.quote,
                locator=EvidenceLocator(
                    char_start=quote_char_start, char_end=quote_char_end
                ),
                interpretation=quote.interpretation,
                confidence=quote.confidence,
                provenance={
                    "builder": "evidence_card_builder",
                    "read_id": read.read_id,
                    "read_char_start": read.char_start,
                    "read_char_end": read.char_end,
                    "quote_char_start": quote_char_start,
                    "quote_char_end": quote_char_end,
                    **(
                        {"source_record_id": record.source_record_id}
                        if record is not None
                        else {}
                    ),
                },
            )
            evidence.append(item)
            sources.append(
                EvidenceSource(
                    title=work.title,
                    quote=quote.quote,
                    location=(
                        f"artifact {persisted_artifact.artifact_id} "
                        f"chars:{quote_char_start}-{quote_char_end}"
                    ),
                    doi=_doi(work, record),
                    url=(
                        record.full_text_url or record.landing_url
                        if record is not None
                        else None
                    ),
                )
            )
        return evidence, sources


def _quote_matches(quote: str, text: str) -> bool:
    return quote in text or _normalize_whitespace(quote) in _normalize_whitespace(text)


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


_WS_RE = re.compile(r"\s")


def _normalized_spans(value: str) -> tuple[str, list[tuple[int, int]]]:
    """Collapse whitespace like _normalize_whitespace while keeping original offsets."""

    chars: list[str] = []
    spans: list[tuple[int, int]] = []
    index = 0
    while index < len(value):
        if _WS_RE.match(value[index]):
            end = index + 1
            while end < len(value) and _WS_RE.match(value[end]):
                end += 1
            chars.append(" ")
            spans.append((index, end))
            index = end
        else:
            chars.append(value[index])
            spans.append((index, index + 1))
            index += 1
    return "".join(chars), spans


def _find_quote_span(quote: str, text: str) -> tuple[int, int]:
    """Return the original character span of *quote* inside *text*.

    Exact substring matches are preferred. Whitespace-normalized matches are
    mapped back to original offsets so Evidence.locator always refers to the
    persisted Reader text, never to a normalized copy.
    """

    exact = text.find(quote)
    if exact >= 0:
        return exact, exact + len(quote)

    normalized_text, spans = _normalized_spans(text)
    wanted = _normalize_whitespace(quote)
    normalized_start = normalized_text.find(wanted)
    if normalized_start < 0:
        raise ValueError(f"quote not found in read text: {quote!r}")
    normalized_end = normalized_start + len(wanted)
    if normalized_end > len(spans):
        raise ValueError(f"quote span out of bounds: {quote!r}")
    return spans[normalized_start][0], spans[normalized_end - 1][1]


def _resolve_source_record(
    artifact: Artifact,
    work: Work,
    records: dict[str, SourceRecord],
) -> SourceRecord | None:
    if artifact.source_record_id is not None:
        return records.get(artifact.source_record_id)
    if work.canonical_source_record_id is not None:
        canonical = records.get(work.canonical_source_record_id)
        if canonical is not None:
            return canonical
    candidates = sorted(
        (item for item in records.values() if item.work_id == work.work_id),
        key=lambda item: item.source_record_id,
    )
    return candidates[0] if candidates else None


def _doi(work: Work, record: SourceRecord | None) -> str | None:
    work_doi = next(
        (item.value for item in work.identifiers if item.namespace == "doi"), None
    )
    if work_doi is not None:
        return work_doi
    if record is None:
        return None
    return next(
        (item.value for item in record.identifiers if item.namespace == "doi"), None
    )


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()
    return f"{prefix}_{digest[:24]}"
