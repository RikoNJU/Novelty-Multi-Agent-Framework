from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactRole,
    ContentExtent,
    Evidence,
    EvidenceLocator,
    ExternalIdentifier,
    ReferenceManifest,
    ResearchBundle,
    SearchExecution,
    SearchExecutionStatus,
    SearchResultRef,
    SourceKind,
    SourceRecord,
    Work,
    WorkType,
)

NOW = datetime(2026, 8, 17, tzinfo=timezone.utc)
SHA = "A" * 64


def make_work(**updates):
    data = {
        "work_id": "wrk_001",
        "work_type": WorkType.ARTICLE,
        "title": "A paper",
        "authors": ["Author One"],
        "publication_year": 2025,
        "identifiers": [{"namespace": "DOI", "value": "10.1/example"}],
    }
    data.update(updates)
    return Work(**data)


def make_record(record_id="src_001", **updates):
    data = {
        "source_record_id": record_id,
        "work_id": "wrk_001",
        "source_id": "arxiv",
        "source_kind": SourceKind.STRUCTURED_DATABASE,
        "external_id": "2501.00001v2",
        "title": "A paper",
        "access_status": AccessStatus.FULL_TEXT_ACQUIRED,
        "observed_at": NOW,
    }
    data.update(updates)
    return SourceRecord(**data)


def make_artifact(artifact_id="art_pdf", **updates):
    extension = "md" if artifact_id.endswith("md") else "pdf"
    data = {
        "artifact_id": artifact_id,
        "work_id": "wrk_001",
        "source_record_id": "src_001",
        "role": ArtifactRole.FULL_TEXT,
        "media_type": "application/pdf",
        "relative_path": f"documents/wrk_001/{artifact_id}.{extension}",
        "sha256": SHA,
        "content_extent": ContentExtent.FULL,
        "acquired_at": NOW,
    }
    data.update(updates)
    return Artifact(**data)


def test_minimal_models_and_json_round_trip():
    identifier = ExternalIdentifier(namespace=" DOI ", value=" 10.1/example ")
    assert identifier.namespace == "doi"
    work = make_work(identifiers=[identifier])
    record = make_record()
    artifact = make_artifact()
    locator = EvidenceLocator(page_start=1)
    evidence = Evidence(
        evidence_id="ev_1",
        work_id=work.work_id,
        artifact_id=artifact.artifact_id,
        quote="original text",
        locator=locator,
        interpretation="supports the claim",
        confidence=0.8,
    )
    execution = SearchExecution(
        execution_id="exec_1",
        tool_name="search",
        source_id="arxiv",
        query="query",
        status=SearchExecutionStatus.SUCCEEDED,
        started_at=NOW,
        completed_at=NOW,
        results=[SearchResultRef(source_record_id=record.source_record_id, rank=1)],
    )
    bundle = ResearchBundle(
        bundle_id="bundle_1",
        producer="test",
        search_executions=[execution],
        works=[work],
        source_records=[record],
        artifacts=[artifact],
        evidence=[evidence],
    )
    assert ResearchBundle.model_validate(bundle.model_dump(mode="json")) == bundle


@pytest.mark.parametrize(
    ("factory", "update"),
    [
        (make_work, {"title": " "}),
        (make_work, {"publication_year": 999}),
        (make_record, {"observed_at": datetime(2026, 1, 1)}),
        (make_artifact, {"acquired_at": datetime(2026, 1, 1)}),
        (make_artifact, {"sha256": "bad"}),
    ],
)
def test_invalid_common_fields_are_rejected(factory, update):
    with pytest.raises(ValidationError):
        factory(**update)


def test_duplicate_external_identifiers_are_rejected():
    with pytest.raises(ValidationError, match="duplicate external identifier"):
        make_work(
            identifiers=[
                {"namespace": "DOI", "value": "same"},
                {"namespace": "doi", "value": "same"},
            ]
        )


@pytest.mark.parametrize("path", ["/tmp/a.pdf", "../a.pdf", "a.pdf", "documents/../a.pdf", r"documents\w\a.pdf"])
def test_artifact_rejects_unsafe_paths(path):
    with pytest.raises(ValidationError, match="relative_path"):
        make_artifact(relative_path=path)


def test_artifact_normalizes_sha256():
    assert make_artifact().sha256 == SHA.lower()


@pytest.mark.parametrize(
    ("artifact_id", "updates"),
    [
        ("art_pdf", {"relative_path": "documents/wrk_001/other.pdf"}),
        ("art_pdf", {"relative_path": "documents/wrk_001/nested/art_pdf.pdf"}),
        ("art_pdf", {"relative_path": "documents/wrk_001/art_pdf.md"}),
    ],
)
def test_artifact_path_matches_identity_and_media_type(artifact_id, updates):
    with pytest.raises(ValidationError, match="relative_path"):
        make_artifact(artifact_id, **updates)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"page_end": 2},
        {"page_start": 2, "page_end": 1},
        {"paragraph_start": 0},
        {"char_start": -1},
    ],
)
def test_evidence_locator_rejects_invalid_locations(data):
    with pytest.raises(ValidationError):
        EvidenceLocator(**data)


def test_evidence_confidence_is_bounded():
    with pytest.raises(ValidationError):
        Evidence(
            evidence_id="ev", work_id="w", artifact_id="a", quote="q",
            locator={"section": "intro"}, interpretation="i", confidence=1.1,
        )


def test_search_execution_validates_time_and_unique_results():
    with pytest.raises(ValidationError, match="completed_at"):
        SearchExecution(
            execution_id="e", tool_name="t", source_id="s", query="q",
            status="failed", started_at=NOW,
            completed_at=datetime(2026, 8, 16, tzinfo=timezone.utc),
        )
    with pytest.raises(ValidationError, match="duplicate rank"):
        SearchExecution(
            execution_id="e", tool_name="t", source_id="s", query="q",
            status="succeeded", started_at=NOW,
            results=[
                {"source_record_id": "s1", "rank": 1},
                {"source_record_id": "s2", "rank": 1},
            ],
        )
    with pytest.raises(ValidationError, match="duplicate source_record_id"):
        SearchExecution(
            execution_id="e", tool_name="t", source_id="s", query="q",
            status="succeeded", started_at=NOW,
            results=[
                {"source_record_id": "s1", "rank": 1},
                {"source_record_id": "s1", "rank": 2},
            ],
        )


def test_complete_manifest_with_two_records_and_derived_artifact_round_trips():
    pdf = make_artifact()
    markdown = make_artifact(
        "art_md",
        source_record_id="src_002",
        role="extracted_text",
        media_type="text/markdown",
        derived_from_artifact_id=pdf.artifact_id,
    )
    manifest = ReferenceManifest(
        subject_paper_id="subject",
        updated_at=NOW,
        works=[make_work(canonical_source_record_id="src_001")],
        source_records=[make_record(), make_record("src_002", external_id="web-1")],
        artifacts=[pdf, markdown],
    )
    assert ReferenceManifest.model_validate(manifest.model_dump(mode="json")) == manifest


@pytest.mark.parametrize(
    "works,records,artifacts,message",
    [
        ([make_work(), make_work()], [make_record()], [make_artifact()], "duplicate work_id"),
        ([make_work(canonical_source_record_id="missing")], [make_record()], [make_artifact()], "canonical_source_record_id"),
        ([make_work()], [make_record(work_id="missing")], [], "source_record src_001.work_id"),
        ([make_work()], [make_record()], [make_artifact(work_id="missing", relative_path="documents/missing/art_pdf.pdf")], "artifact art_pdf.work_id"),
        ([make_work()], [make_record()], [make_artifact(), make_artifact().model_copy(update={"artifact_id": "art_2"})], "relative_path"),
        ([make_work()], [make_record()], [make_artifact(derived_from_artifact_id="art_pdf")], "self-reference"),
    ],
)
def test_manifest_rejects_broken_references(works, records, artifacts, message):
    with pytest.raises(ValidationError, match=message):
        ReferenceManifest(subject_paper_id="subject", updated_at=NOW, works=works, source_records=records, artifacts=artifacts)


def test_manifest_rejects_derived_cycles_and_acquired_record_without_artifact():
    first = make_artifact("a", derived_from_artifact_id="b")
    second = make_artifact("b", derived_from_artifact_id="a")
    with pytest.raises(ValidationError, match="cycle"):
        ReferenceManifest(subject_paper_id="subject", updated_at=NOW, works=[make_work()], source_records=[make_record()], artifacts=[first, second])
    with pytest.raises(ValidationError, match="has no artifact"):
        ReferenceManifest(subject_paper_id="subject", updated_at=NOW, works=[make_work()], source_records=[make_record()])


def test_json_metadata_rejects_non_serializable_values():
    with pytest.raises(ValidationError, match="non-JSON-compatible"):
        make_record(raw_metadata={"bad": object()})
    with pytest.raises(ValidationError, match="non-finite"):
        make_record(raw_metadata={"bad": float("nan")})
