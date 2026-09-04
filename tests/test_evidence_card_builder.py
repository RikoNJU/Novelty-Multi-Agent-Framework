"""Deterministic EvidenceCardBuilder provenance and identity tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from novelty_agent_framework.agents import DefaultEvidenceValidator
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactRole,
    ContentExtent,
    EvidenceCardDraft,
    EvidenceLocator,
    EvidenceQuoteDraft,
    ExternalIdentifier,
    NoveltyPoint,
    ReferenceReadResult,
    ResearchFinishDraft,
    ResearchTask,
    SourceKind,
    SourceRecord,
    TaskResearchRequest,
    Work,
    WorkType,
)
from novelty_agent_framework.tools import EvidenceCardBuilder, ResearcherToolRegistry
from conftest import minimal_search_plan

NOW = datetime(2026, 8, 25, tzinfo=timezone.utc)
SHA = "a" * 64
TEXT_A = "Alpha unique quote. Shared technical statement. Another A quote."
TEXT_B = "Beta unique quote. Shared technical statement. Another B quote."


def scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id="paper-1",
        run_id="run-builder",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="claim", technical_features=["feature"]
        ),
        research_task=ResearchTask(
            task_id="TASK-1",
            novelty_point_id="NP-1",
            task_type="evidence",
            language="en",
        ),
        search_plan=minimal_search_plan("TASK-1", "NP-1"),
    )


def prepare_store(tmp_path) -> ReferenceStore:
    store = ReferenceStore(tmp_path)
    manifest = store.load_manifest("paper-1")
    works = [
        Work(
            work_id="wrk_a",
            work_type=WorkType.WEBPAGE,
            title="Trusted Work A",
            identifiers=[ExternalIdentifier(namespace="doi", value="10.1/work-a")],
            canonical_source_record_id="src_a",
        ),
        Work(work_id="wrk_b", work_type=WorkType.WEBPAGE, title="Trusted Work B"),
    ]
    records = [
        SourceRecord(
            source_record_id="src_a",
            work_id="wrk_a",
            source_id="test",
            source_kind=SourceKind.WEB,
            title="Source A",
            landing_url="https://landing.example/a",
            full_text_url="https://full.example/a",
            access_status=AccessStatus.FULL_TEXT_ACQUIRED,
            observed_at=NOW,
        ),
        SourceRecord(
            source_record_id="src_b",
            work_id="wrk_b",
            source_id="test",
            source_kind=SourceKind.WEB,
            title="Source B",
            landing_url="https://landing.example/b",
            identifiers=[ExternalIdentifier(namespace="doi", value="10.1/source-b")],
            access_status=AccessStatus.FULL_TEXT_ACQUIRED,
            observed_at=NOW,
        ),
    ]
    artifacts = [
        Artifact(
            artifact_id="art_a",
            work_id="wrk_a",
            source_record_id="src_a",
            role=ArtifactRole.EXTRACTED_TEXT,
            media_type="text/plain",
            relative_path="documents/wrk_a/art_a.txt",
            sha256=SHA,
            content_extent=ContentExtent.FULL,
            acquired_at=NOW,
        ),
        Artifact(
            artifact_id="art_b",
            work_id="wrk_b",
            source_record_id="src_b",
            role=ArtifactRole.EXTRACTED_TEXT,
            media_type="text/plain",
            relative_path="documents/wrk_b/art_b.txt",
            sha256="b" * 64,
            content_extent=ContentExtent.FULL,
            acquired_at=NOW,
        ),
    ]
    store.persist_manifest(
        "paper-1",
        manifest.model_copy(
            update={"works": works, "source_records": records, "artifacts": artifacts}
        ),
    )
    return store


def read(work="wrk_a", artifact="art_a", text=TEXT_A, **updates):
    values = {
        "read_id": f"read_{work}",
        "work_id": work,
        "artifact_id": artifact,
        "role": ArtifactRole.EXTRACTED_TEXT,
        "char_start": 0,
        "char_end": len(text),
        "text": text,
        "has_more": False,
        "sha256": SHA,
    }
    values.update(updates)
    return ReferenceReadResult(**values)


def quote(text, interpretation="meaning"):
    return EvidenceQuoteDraft(
        quote=text, interpretation=interpretation, confidence=0.9
    )


def card(*quotes):
    return EvidenceCardDraft(
        main_contribution="Model semantic contribution",
        overlaps=["overlap"],
        differences=["difference"],
        quotes=list(quotes),
        possible_baseline=True,
        relevance=0.8,
        confidence=0.9,
    )


def finish(*cards):
    return ResearchFinishDraft(cards=list(cards))


def builder(tmp_path):
    return EvidenceCardBuilder(prepare_store(tmp_path))


def test_single_quote_builds_trusted_card_and_evidence(tmp_path) -> None:
    result = builder(tmp_path).build(
        finish(card(quote("Alpha unique quote."))),
        scope=scope(),
        read_results=[read()],
    )

    assert len(result.evidence) == len(result.evidence_cards) == 1
    evidence = result.evidence[0]
    built = result.evidence_cards[0]
    assert (evidence.task_id, evidence.novelty_point_id) == ("TASK-1", "NP-1")
    assert (evidence.work_id, evidence.artifact_id) == ("wrk_a", "art_a")
    assert evidence.locator == EvidenceLocator(char_start=0, char_end=19)
    assert evidence.provenance == {
        "builder": "evidence_card_builder",
        "read_id": "read_wrk_a",
        "read_char_start": 0,
        "read_char_end": len(TEXT_A),
        "quote_char_start": 0,
        "quote_char_end": 19,
        "source_record_id": "src_a",
    }
    assert built.document_title == "Trusted Work A"
    assert built.sources[0].url == "https://full.example/a"
    assert built.sources[0].doi == "10.1/work-a"
    assert built.sources[0].location == "artifact art_a chars:0-19"
    assert built.cited_by_paper is None
    assert built.evidence_ids == [evidence.evidence_id]


def test_locator_uses_absolute_read_offset(tmp_path) -> None:
    result = builder(tmp_path).build(
        finish(card(quote("Alpha unique quote."))),
        scope=scope(),
        read_results=[read(char_start=100, char_end=100 + len(TEXT_A))],
    )

    evidence = result.evidence[0]
    source = result.evidence_cards[0].sources[0]
    assert evidence.locator == EvidenceLocator(char_start=100, char_end=119)
    assert evidence.provenance["quote_char_start"] == 100
    assert evidence.provenance["quote_char_end"] == 119
    assert source.location == "artifact art_a chars:100-119"


def test_whitespace_normalized_quote_maps_to_original_offsets(tmp_path) -> None:
    prefix = "prefix\n"
    segment = "Alpha \t unique\nquote."
    text = prefix + segment + " suffix"
    result = builder(tmp_path).build(
        finish(card(quote("Alpha   unique\nquote."))),
        scope=scope(),
        read_results=[read(text=text, char_start=500, char_end=500 + len(text))],
    )

    evidence = result.evidence[0]
    expected_start = 500 + len(prefix)
    expected_end = 500 + len(prefix) + len(segment)
    assert evidence.locator == EvidenceLocator(
        char_start=expected_start, char_end=expected_end
    )
    assert text[evidence.locator.char_start - 500 : evidence.locator.char_end - 500] == segment
    assert result.evidence_cards[0].sources[0].location == (
        f"artifact art_a chars:{expected_start}-{expected_end}"
    )


def test_evidence_locators_stay_inside_read_bounds(tmp_path) -> None:
    result = builder(tmp_path).build(
        finish(card(quote("Alpha unique quote."), quote("Another A quote."))),
        scope=scope(),
        read_results=[read(char_start=10, char_end=10 + len(TEXT_A))],
    )
    for evidence in result.evidence:
        assert evidence.locator is not None
        assert evidence.locator.char_start >= 10
        assert evidence.locator.char_end <= 10 + len(TEXT_A)

def test_built_card_passes_default_evidence_validator(tmp_path) -> None:
    result = builder(tmp_path).build(
        finish(card(quote("Alpha unique quote."))),
        scope=scope(),
        read_results=[read()],
    )
    validation = DefaultEvidenceValidator().validate(
        result.evidence_cards, tasks=[scope().research_task]
    )
    assert [card.card_id for card in validation.accepted] == [
        result.evidence_cards[0].card_id
    ]
    assert validation.rejected == ()

def test_multiple_reads_quotes_and_whitespace_grounding(tmp_path) -> None:
    duplicate = read(
        read_id="read_later",
        char_start=10,
        char_end=10 + len(TEXT_A),
    )
    result = builder(tmp_path).build(
        finish(
            card(
                quote("Alpha   unique\nquote."),
                quote("Another A quote."),
            )
        ),
        scope=scope(),
        read_results=[duplicate, read()],
    )

    assert len(result.evidence) == 2
    assert {item.work_id for item in result.evidence} == {"wrk_a"}
    assert all(item.provenance["read_id"] == "read_wrk_a" for item in result.evidence)


def test_ungrounded_cross_work_and_ambiguous_quotes_fail(tmp_path) -> None:
    compiler = builder(tmp_path)
    reads = [read(), read("wrk_b", "art_b", TEXT_B)]
    with pytest.raises(ValueError, match="ungrounded quote"):
        compiler.build(
            finish(card(quote("Paraphrased but absent"))),
            scope=scope(), read_results=reads,
        )
    with pytest.raises(ValueError, match="cross-work"):
        compiler.build(
            finish(card(quote("Alpha unique quote."), quote("Beta unique quote."))),
            scope=scope(), read_results=reads,
        )
    with pytest.raises(ValueError, match="ambiguous"):
        compiler.build(
            finish(card(quote("Shared technical statement."))),
            scope=scope(), read_results=reads,
        )


def test_candidate_intersection_disambiguates_shared_quote(tmp_path) -> None:
    result = builder(tmp_path).build(
        finish(card(quote("Shared technical statement."), quote("Alpha unique quote."))),
        scope=scope(),
        read_results=[read(), read("wrk_b", "art_b", TEXT_B)],
    )
    assert result.evidence_cards[0].document_title == "Trusted Work A"
    assert {item.work_id for item in result.evidence} == {"wrk_a"}


def test_missing_or_mismatched_artifact_fails_explicitly(tmp_path) -> None:
    compiler = builder(tmp_path)
    with pytest.raises(ValueError, match="missing Artifact"):
        compiler.build(
            finish(card(quote("Alpha unique quote."))),
            scope=scope(), read_results=[read(artifact="art_missing")],
        )
    with pytest.raises(ValueError, match="Artifact.work_id mismatch"):
        compiler.build(
            finish(card(quote("Alpha unique quote."))),
            scope=scope(), read_results=[read(work="wrk_b", artifact="art_a")],
        )


def test_duplicate_work_drafts_are_rejected(tmp_path) -> None:
    duplicate = card(quote("Alpha unique quote."))
    with pytest.raises(ValueError, match="duplicate evidence card for work"):
        builder(tmp_path).build(
            finish(duplicate, duplicate), scope=scope(), read_results=[read()]
        )


def test_ids_and_duplicate_read_selection_are_deterministic(tmp_path) -> None:
    compiler = builder(tmp_path)
    draft = finish(card(quote("Alpha unique quote.")))
    reads = [
        read(read_id="read_z", char_start=0, char_end=len(TEXT_A)),
        read(read_id="read_a", char_start=0, char_end=len(TEXT_A)),
    ]
    first = compiler.build(draft, scope=scope(), read_results=reads)
    second = compiler.build(draft, scope=scope(), read_results=reversed(reads))
    assert first.evidence[0].evidence_id == second.evidence[0].evidence_id
    assert first.evidence_cards[0].card_id == second.evidence_cards[0].card_id
    assert first.evidence[0].provenance["read_id"] == "read_a"


def test_source_doi_fallback_and_model_cannot_override_metadata(tmp_path) -> None:
    result = builder(tmp_path).build(
        finish(card(quote("Beta unique quote."))),
        scope=scope(), read_results=[read("wrk_b", "art_b", TEXT_B)],
    )
    source = result.evidence_cards[0].sources[0]
    assert result.evidence_cards[0].document_title == "Trusted Work B"
    assert source.url == "https://landing.example/b"
    assert source.doi == "10.1/source-b"
    assert not {
        "work_id", "artifact_id", "source_record_id", "url", "doi", "document_title"
    }.intersection(EvidenceCardDraft.model_fields)


def test_no_evidence_finish_and_registry_boundary(tmp_path) -> None:
    compiler = builder(tmp_path)
    result = compiler.build(
        ResearchFinishDraft(cards=[], no_evidence_reason="No grounded source"),
        scope=scope(), read_results=[],
    )
    assert result.evidence == result.evidence_cards == []
    assert result.warnings == ["no evidence: No grounded source"]
    assert "evidence_card_builder" not in ResearcherToolRegistry().names
