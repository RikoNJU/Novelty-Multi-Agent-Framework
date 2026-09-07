from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from novelty_agent_framework.persistence import ReferenceStore, SubjectReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactNamespace,
    ArtifactRole,
    ContentExtent,
    ReferenceManifest,
    SourceKind,
    SourceRecord,
    Work,
)
from scripts.reference_namespace_diagnostics import inspect_workspace


NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)
PAPER_ID = "paper-diagnostics"


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _put(store: ReferenceStore, *, work_id: str, text: str) -> None:
    artifact_id = "artifact_same"
    source_id = f"src_{work_id}"
    work = Work(work_id=work_id, work_type="article", title=work_id)
    record = SourceRecord(
        source_record_id=source_id,
        work_id=work_id,
        source_id="diagnostics-test",
        source_kind=SourceKind.LOCAL,
        title=work_id,
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


def _workspace(tmp_path: Path) -> Path:
    output_root = tmp_path / "outputs"
    _put(ReferenceStore(output_root), work_id="research_work", text="SECRET RESEARCH")
    _put(
        SubjectReferenceStore(output_root),
        work_id="subject_work",
        text="SECRET SUBJECT",
    )
    workspace = output_root / PAPER_ID
    _write(
        workspace / "runtime/run-1/tools/0001_reader.json",
        {
            "tool_name": "reader",
            "execution_status": "SUCCESS",
            "resolved_arguments": {
                "namespace": "subject_reference",
                "artifact_id": "artifact_same",
            },
            "raw_result": {
                "payload": {
                    "read_result": {
                        "namespace": "subject_reference",
                        "artifact_id": "artifact_same",
                        "text": "SECRET SUBJECT",
                    }
                }
            },
        },
    )
    _write(
        workspace / "research-runs/NP-1/T-1/attempt-1.json",
        {
            "evidence": [
                {
                    "evidence_id": "evidence-1",
                    "artifact_id": "artifact_same",
                    "quote": "SECRET SUBJECT",
                    "provenance": {"artifact_namespace": "subject_reference"},
                }
            ]
        },
    )
    return workspace


def test_diagnostics_reports_closed_chain_and_allowed_collision(tmp_path) -> None:
    workspace = _workspace(tmp_path)
    report = inspect_workspace(
        workspace,
        namespace=ArtifactNamespace.SUBJECT_REFERENCE,
        artifact_id="artifact_same",
    )

    assert report["ok"] is True
    assert report["artifact_id_collisions"] == ["artifact_same"]
    assert report["address_lookup"]["found"] is True
    assert report["reader_calls"][0]["namespace_match"] is True
    assert report["evidence_bindings"][0]["resolved"] is True
    serialized = json.dumps(report)
    assert "SECRET RESEARCH" not in serialized
    assert "SECRET SUBJECT" not in serialized


def test_diagnostics_finds_reader_and_evidence_namespace_breaks(tmp_path) -> None:
    workspace = _workspace(tmp_path)
    reader_path = workspace / "runtime/run-1/tools/0001_reader.json"
    reader = json.loads(reader_path.read_text(encoding="utf-8"))
    reader["raw_result"]["payload"]["read_result"]["namespace"] = (
        "research_reference"
    )
    _write(reader_path, reader)
    attempt_path = workspace / "research-runs/NP-1/T-1/attempt-1.json"
    attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    attempt["evidence"][0]["provenance"].pop("artifact_namespace")
    _write(attempt_path, attempt)

    report = inspect_workspace(workspace)

    assert report["ok"] is False
    assert any("Reader namespace mismatch" in item for item in report["errors"])
    assert any(
        "Evidence missing or invalid artifact_namespace" in item
        for item in report["errors"]
    )


def test_diagnostics_requires_and_resolves_complete_address(tmp_path) -> None:
    workspace = _workspace(tmp_path)
    with pytest.raises(ValueError, match="provided together"):
        inspect_workspace(workspace, artifact_id="artifact_same")

    report = inspect_workspace(
        workspace,
        namespace=ArtifactNamespace.SUBJECT_REFERENCE,
        artifact_id="missing",
    )
    assert report["ok"] is False
    assert report["address_lookup"]["found"] is False
    assert any("unknown artifact address" in item for item in report["errors"])
