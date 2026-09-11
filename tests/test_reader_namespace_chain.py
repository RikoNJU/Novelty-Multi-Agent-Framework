"""Reader-to-builder artifact address continuity across reference namespaces."""

from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from novelty_agent_framework.persistence import ReferenceStore, SubjectReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactNamespace,
    ArtifactRole,
    ContentExtent,
    EvidenceCardDraft,
    EvidenceQuoteDraft,
    NoveltyPoint,
    ReaderArguments,
    ReferenceManifest,
    ReferenceSearchArguments,
    ResearchFinishDraft,
    ResearchTask,
    SourceKind,
    SourceRecord,
    TaskResearchRequest,
    Work,
)
from novelty_agent_framework.tools import (
    EvidenceCardBuilder,
    ReaderTool,
    ReferenceArtifactReaderTool,
    ReferenceSearchTool,
)
from novelty_agent_framework.workflows.research_task import _trusted_reads
from conftest import minimal_search_plan


NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)
PAPER_ID = "paper-namespaces"


def _scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id=PAPER_ID,
        run_id="run-namespaces",
        novelty_point=NoveltyPoint(
            point_id="NP-NS", claim="namespace continuity", technical_features=[]
        ),
        research_task=ResearchTask(
            task_id="TASK-NS",
            novelty_point_id="NP-NS",
            task_type="evidence",
            language="en",
        ),
        search_plan=minimal_search_plan("TASK-NS", "NP-NS"),
    )


def _put(
    store: ReferenceStore,
    *,
    work_id: str,
    artifact_id: str,
    title: str,
    text: str,
) -> None:
    source_id = f"src_{work_id}"
    work = Work(work_id=work_id, work_type="article", title=title)
    record = SourceRecord(
        source_record_id=source_id,
        work_id=work_id,
        source_id="namespace-test",
        source_kind=SourceKind.LOCAL,
        title=title,
        abstract=text,
        access_status=AccessStatus.FULL_TEXT_ACQUIRED,
        observed_at=NOW,
    )
    store.write_document(
        PAPER_ID,
        work_id=work_id,
        artifact_id=artifact_id,
        extension="txt",
        content=text,
    )
    artifact = Artifact(
        artifact_id=artifact_id,
        work_id=work_id,
        source_record_id=source_id,
        role=ArtifactRole.EXTRACTED_TEXT,
        media_type="text/plain",
        relative_path=f"documents/{work_id}/{artifact_id}.txt",
        sha256=hashlib.sha256(text.encode()).hexdigest(),
        content_extent=ContentExtent.FULL,
        acquired_at=NOW,
    )
    store.persist_manifest(
        PAPER_ID,
        ReferenceManifest(
            subject_paper_id=PAPER_ID,
            updated_at=NOW,
            works=[work],
            source_records=[record],
            artifacts=[artifact],
        ),
    )


def _draft(quote: str) -> ResearchFinishDraft:
    return ResearchFinishDraft(
        cards=[
            EvidenceCardDraft(
                main_contribution="grounded contribution",
                quotes=[
                    EvidenceQuoteDraft(
                        quote=quote,
                        interpretation="grounded interpretation",
                        confidence=0.9,
                    )
                ],
                relevance=0.8,
                confidence=0.9,
            )
        ]
    )


def _read(
    root,
    namespace: ArtifactNamespace,
    artifact_id: str,
):
    reader = ReaderTool(ReferenceArtifactReaderTool(ReferenceStore(root)))
    observation = asyncio.run(
        reader.ainvoke(
            ReaderArguments(namespace=namespace, artifact_id=artifact_id),
            scope=_scope(),
        )
    )
    return observation, observation.payload["read_result"]


def test_a_research_reference_reader_and_builder_baseline(tmp_path) -> None:
    research = ReferenceStore(tmp_path)
    _put(
        research,
        work_id="work_a",
        artifact_id="artifact_a",
        title="Research A",
        text="RESEARCH A QUOTE",
    )

    _observation, payload = _read(
        tmp_path, ArtifactNamespace.RESEARCH_REFERENCE, "artifact_a"
    )
    assert payload["namespace"] == "research_reference"
    assert payload["artifact_id"] == "artifact_a"
    assert payload["work_id"] == "work_a"

    result = EvidenceCardBuilder(research).build(
        _draft("RESEARCH A QUOTE"),
        scope=_scope(),
        read_results=[payload],
    )
    assert len(result.evidence_cards) == len(result.evidence) == 1


def test_b_subject_search_reader_builder_chain(tmp_path) -> None:
    subject = SubjectReferenceStore(tmp_path)
    _put(
        subject,
        work_id="work_b",
        artifact_id="artifact_b",
        title="Subject B searchable",
        text="SUBJECT B QUOTE",
    )

    found = ReferenceSearchTool(subject).search(
        PAPER_ID, ReferenceSearchArguments(query="searchable")
    )
    handle = found.results[0].artifact_handles[0]
    assert handle.namespace == ArtifactNamespace.SUBJECT_REFERENCE

    _observation, payload = _read(tmp_path, handle.namespace, handle.artifact_id)
    result = EvidenceCardBuilder(ReferenceStore(tmp_path)).build(
        _draft("SUBJECT B QUOTE"),
        scope=_scope(),
        read_results=[payload],
    )
    assert result.evidence_cards[0].document_title == "Subject B searchable"
    assert result.evidence[0].provenance["artifact_namespace"] == "subject_reference"


def test_c_same_artifact_id_is_read_from_requested_namespace(tmp_path) -> None:
    _put(
        ReferenceStore(tmp_path),
        work_id="research_work",
        artifact_id="artifact_same",
        title="Research collision",
        text="RESEARCH CONTENT",
    )
    _put(
        SubjectReferenceStore(tmp_path),
        work_id="subject_work",
        artifact_id="artifact_same",
        title="Subject collision",
        text="SUBJECT CONTENT",
    )

    _subject_observation, subject = _read(
        tmp_path, ArtifactNamespace.SUBJECT_REFERENCE, "artifact_same"
    )
    _research_observation, research = _read(
        tmp_path, ArtifactNamespace.RESEARCH_REFERENCE, "artifact_same"
    )
    assert subject["text"] == "SUBJECT CONTENT"
    assert research["text"] == "RESEARCH CONTENT"
    assert subject["read_id"] != research["read_id"]


def test_d_wrong_namespace_fails_without_fallback(tmp_path) -> None:
    _put(
        SubjectReferenceStore(tmp_path),
        work_id="subject_only",
        artifact_id="artifact_x",
        title="Subject only",
        text="ONLY SUBJECT",
    )

    with pytest.raises(ValueError, match="unknown artifact_id"):
        _read(tmp_path, ArtifactNamespace.RESEARCH_REFERENCE, "artifact_x")


def test_e_harness_trace_preserves_both_read_namespaces(tmp_path) -> None:
    _put(
        ReferenceStore(tmp_path),
        work_id="research_work",
        artifact_id="research_artifact",
        title="Research trace",
        text="RESEARCH TRACE",
    )
    _put(
        SubjectReferenceStore(tmp_path),
        work_id="subject_work",
        artifact_id="subject_artifact",
        title="Subject trace",
        text="SUBJECT TRACE",
    )
    research_observation, _payload = _read(
        tmp_path, ArtifactNamespace.RESEARCH_REFERENCE, "research_artifact"
    )
    subject_observation, _payload = _read(
        tmp_path, ArtifactNamespace.SUBJECT_REFERENCE, "subject_artifact"
    )
    trace = [
        SimpleNamespace(kind="tool_result", observation=research_observation),
        SimpleNamespace(kind="tool_result", observation=subject_observation),
    ]

    reads, warnings = _trusted_reads(trace)
    assert warnings == []
    assert [read.namespace for read in reads] == [
        ArtifactNamespace.RESEARCH_REFERENCE,
        ArtifactNamespace.SUBJECT_REFERENCE,
    ]

    projected = ReaderTool(
        ReferenceArtifactReaderTool(ReferenceStore(tmp_path))
    ).project_model_context(subject_observation)
    assert projected["read_result"]["namespace"] == "subject_reference"
