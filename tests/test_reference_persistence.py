import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

import novelty_agent_framework.persistence as persistence
from novelty_agent_framework.persistence import (
    load_reference_manifest,
    paper_workspace,
    persist_reference_manifest,
    reference_documents_dir,
    reference_workspace,
)
from novelty_agent_framework.schemas import ReferenceManifest


def test_workspace_initializes_empty_reference_manifest(tmp_path):
    workspace = paper_workspace("paper-1", output_root=tmp_path)
    assert reference_workspace("paper-1", output_root=tmp_path) == workspace / "references"
    assert reference_documents_dir("paper-1", output_root=tmp_path).is_dir()
    manifest = load_reference_manifest("paper-1", output_root=tmp_path)
    assert manifest.subject_paper_id == "paper-1"
    assert manifest.works == []


def test_repeated_workspace_initialization_does_not_overwrite_manifest(tmp_path):
    path = paper_workspace("paper-1", output_root=tmp_path) / "references/list.json"
    path.write_text('{"custom": true}\n', encoding="utf-8")
    paper_workspace("paper-1", output_root=tmp_path)
    assert path.read_text(encoding="utf-8") == '{"custom": true}\n'


def test_manifest_save_load_round_trip_and_no_temporary_files(tmp_path):
    manifest = ReferenceManifest(
        subject_paper_id="论文-1",
        updated_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
    )
    path = persist_reference_manifest("论文-1", manifest, output_root=tmp_path)
    assert load_reference_manifest("论文-1", output_root=tmp_path) == manifest
    assert json.loads(path.read_text(encoding="utf-8"))["subject_paper_id"] == "论文-1"
    assert list(path.parent.glob("*.tmp")) == []
    assert list(path.parent.glob(".*.tmp")) == []


def test_manifest_subject_must_match_paper_id(tmp_path):
    manifest = ReferenceManifest(
        subject_paper_id="other",
        updated_at=datetime.now(timezone.utc),
    )
    with pytest.raises(ValueError, match="does not match"):
        persist_reference_manifest("paper-1", manifest, output_root=tmp_path)


def test_failed_atomic_replace_preserves_existing_manifest(tmp_path, monkeypatch):
    original = ReferenceManifest(
        subject_paper_id="paper-1",
        updated_at=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )
    path = persist_reference_manifest("paper-1", original, output_root=tmp_path)
    original_json = path.read_text(encoding="utf-8")
    updated = original.model_copy(
        update={"updated_at": datetime(2026, 8, 17, tzinfo=timezone.utc)}
    )

    def fail_replace(source, destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(persistence.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated"):
        persist_reference_manifest("paper-1", updated, output_root=tmp_path)

    assert path.read_text(encoding="utf-8") == original_json
    assert list(path.parent.glob(".*.tmp")) == []


def test_corrupt_or_invalid_manifest_is_not_silently_replaced(tmp_path):
    path = paper_workspace("paper-1", output_root=tmp_path) / "references/list.json"
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_reference_manifest("paper-1", output_root=tmp_path)
    path.write_text(json.dumps({"subject_paper_id": "paper-1"}), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_reference_manifest("paper-1", output_root=tmp_path)
