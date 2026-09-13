from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from novelty_agent_framework.persistence import (
    ReferenceStore,
    SubjectReferenceStore,
    paper_workspace,
)
from novelty_agent_framework.schemas import (
    Artifact,
    ArtifactRole,
    ContentExtent,
    Work,
    WorkType,
)
from scripts.reader_failure_diagnostics import inspect_run


NOW = datetime(2026, 9, 11, tzinfo=timezone.utc)
PAPER_ID = "paper-reader-diagnostics"


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _artifact(artifact_id: str, work_id: str, content: str) -> Artifact:
    return Artifact(
        artifact_id=artifact_id,
        work_id=work_id,
        role=ArtifactRole.EXTRACTED_TEXT,
        media_type="text/plain",
        relative_path=f"documents/{work_id}/{artifact_id}.txt",
        sha256=hashlib.sha256(content.encode()).hexdigest(),
        byte_size=len(content.encode()),
        content_extent=ContentExtent.FULL,
        acquired_at=NOW,
    )


def _put(store: ReferenceStore, work_id: str, artifact_id: str, content: str) -> None:
    store.write_document(
        PAPER_ID,
        work_id=work_id,
        artifact_id=artifact_id,
        extension="txt",
        content=content,
    )
    store.merge_manifest(
        PAPER_ID,
        works=[Work(work_id=work_id, work_type=WorkType.ARTICLE, title=work_id)],
        artifacts=[_artifact(artifact_id, work_id, content)],
    )


def _reader_call(
    workspace: Path,
    index: int,
    *,
    namespace: str | None,
    artifact_id: str,
    message: str | None,
    run_id: str = "run-1",
) -> None:
    resolved = {
        "artifact_id": artifact_id,
        "char_start": 0,
        "max_chars": 8000,
    }
    if namespace is not None:
        resolved["namespace"] = namespace
    _write(
        workspace / f"runtime/{run_id}/tools/{index:04d}_reader.json",
        {
            "tool_name": "reader",
            "tool_call_id": f"tool_{index:04d}",
            "agent_tool_call_id": f"agent_{index:04d}",
            "stage_name": "run_research_task",
            "execution_status": "FAILED" if message else "SUCCESS",
            "agent_arguments": {"artifact_id": artifact_id},
            "resolved_arguments": resolved,
            "error": ({"type": "ValueError", "message": message} if message else None),
        },
    )


def _workspace(tmp_path: Path) -> Path:
    output_root = tmp_path / "outputs"
    paper_workspace(PAPER_ID, output_root=output_root)
    research = ReferenceStore(output_root)
    subject = SubjectReferenceStore(output_root)

    # 正常制品：manifest 已登记，文件已落盘
    _put(research, "work-ok", "art_ok", "OK")
    # 只存在于论文自带参考语料：按 research namespace 读必然失败（候选 B）
    _put(subject, "work-subject", "art_subject_only", "SUBJECT")
    # 悬空制品：文件已落盘，但 manifest 里没有登记（候选 A 的产物形态）
    research.write_document(
        PAPER_ID,
        work_id="work-orphan",
        artifact_id="art_orphan",
        extension="txt",
        content="ORPHAN",
    )

    workspace = output_root / PAPER_ID
    _reader_call(workspace, 1, namespace="research_reference", artifact_id="art_ok", message=None)
    unknown = "unknown artifact_id {} in the research_reference manifest"
    for index, artifact_id in ((2, "art_subject_only"), (3, "art_orphan"), (4, "art_ghost")):
        _reader_call(
            workspace,
            index,
            namespace="research_reference",
            artifact_id=artifact_id,
            message=unknown.format(repr(artifact_id)),
        )
    return workspace


def _inspect(workspace: Path, run_id: str = "run-1"):
    return inspect_run(workspace, workspace / "runtime" / run_id)


def test_diagnostics_classifies_each_reader_failure(tmp_path) -> None:
    report = _inspect(_workspace(tmp_path))

    assert report["status"] == "WARNING"
    assert report["counts"]["reader_calls"] == 4
    assert report["counts"]["failed"] == 3
    assert report["classification_counts"] == {
        "WRONG_NAMESPACE": 1,
        "LOST_MANIFEST_ENTRY": 1,
        "NEVER_PERSISTED": 1,
    }


def test_diagnostics_prioritises_lost_manifest_entry_in_verdict(tmp_path) -> None:
    report = _inspect(_workspace(tmp_path))

    assert report["verdict"]["primary_code"] == "LOST_MANIFEST_ENTRY"
    orphan = next(
        item for item in report["findings"] if item["artifact_id"] == "art_orphan"
    )
    assert orphan["reason_code"] == "LOST_MANIFEST_ENTRY"
    assert orphan["error_type"] == "ValueError"


def test_diagnostics_reports_missing_runtime_records(tmp_path) -> None:
    workspace = tmp_path / "outputs" / "paper-empty"
    (workspace / "runtime" / "run-empty" / "tools").mkdir(parents=True)

    report = _inspect(workspace, "run-empty")

    assert report["counts"]["reader_calls"] == 0
    assert report["status"] == "INCOMPLETE"
    assert report["classification_counts"] == {}


def test_diagnostics_handles_new_contract_records_without_namespace(tmp_path) -> None:
    """新契约的记录里没有 namespace：工具已同时搜索两个语料，
    未知 id 只可能是「文件在但没登记」或「从未落盘」。"""

    output_root = tmp_path / "outputs"
    paper_workspace(PAPER_ID, output_root=output_root)
    research = ReferenceStore(output_root)
    research.write_document(
        PAPER_ID,
        work_id="work-orphan-new",
        artifact_id="art_orphan_new",
        extension="txt",
        content="ORPHAN",
    )

    workspace = output_root / PAPER_ID
    unknown = "unknown artifact_id {} in the research or subject reference manifest"
    _reader_call(
        workspace, 1, namespace=None, artifact_id="art_orphan_new",
        message=unknown.format(repr("art_orphan_new")),
    )
    _reader_call(
        workspace, 2, namespace=None, artifact_id="art_nowhere",
        message=unknown.format(repr("art_nowhere")),
    )

    report = _inspect(workspace)

    assert report["classification_counts"] == {
        "LOST_MANIFEST_ENTRY": 1,
        "NEVER_PERSISTED": 1,
    }


def test_diagnostics_only_counts_the_selected_run(tmp_path) -> None:
    workspace = _workspace(tmp_path)
    _reader_call(
        workspace,
        1,
        namespace=None,
        artifact_id="other-run-artifact",
        message="unknown artifact_id 'other-run-artifact'",
        run_id="run-2",
    )

    report = _inspect(workspace, "run-1")

    assert report["counts"]["reader_calls"] == 4
    assert all(item["artifact_id"] != "other-run-artifact" for item in report["findings"])


def test_known_reader_errors_are_structurally_classified_and_redacted(tmp_path) -> None:
    workspace = _workspace(tmp_path)
    messages = {
        10: "artifact art_ok sha256 mismatch api_key=top-secret",
        11: "artifact art_ok media_type 'application/pdf' is not readable text",
        12: "artifact art_ok is not valid UTF-8 text",
        13: "char_start 999 exceeds artifact art_ok length",
        14: "reader scope rejected: outside request scope",
        15: "artifact art_ok content file is missing",
    }
    for index, message in messages.items():
        _reader_call(
            workspace,
            index,
            namespace=None,
            artifact_id="art_ok",
            message=message,
            run_id="run-errors",
        )

    report = _inspect(workspace, "run-errors")

    assert report["classification_counts"] == {
        "SHA256_MISMATCH": 1,
        "UNREADABLE_MEDIA_TYPE": 1,
        "UTF8_DECODE_ERROR": 1,
        "CHAR_RANGE_ERROR": 1,
        "SCOPE_REJECTED": 1,
        "MISSING_CONTENT_FILE": 1,
    }
    assert "top-secret" not in json.dumps(report)


def test_corrupt_tool_json_marks_diagnostic_error(tmp_path) -> None:
    workspace = tmp_path / "outputs" / PAPER_ID
    path = workspace / "runtime" / "broken-run" / "tools" / "0001_reader.json"
    path.parent.mkdir(parents=True)
    path.write_text("{broken", encoding="utf-8")

    report = _inspect(workspace, "broken-run")

    assert report["status"] == "ERROR"
    assert report["errors"]


def test_successful_reader_call_passes_and_running_call_warns(tmp_path) -> None:
    workspace = _workspace(tmp_path)
    _reader_call(
        workspace,
        1,
        namespace=None,
        artifact_id="art_ok",
        message=None,
        run_id="success-run",
    )
    assert _inspect(workspace, "success-run")["status"] == "OK"

    running_path = workspace / "runtime" / "running-run" / "tools" / "0001_reader.json"
    _write(
        running_path,
        {
            "tool_name": "reader",
            "tool_call_id": "tool-running",
            "stage_name": "run_research_task",
            "execution_status": "RUNNING",
            "resolved_arguments": {"artifact_id": "art_ok"},
        },
    )
    report = _inspect(workspace, "running-run")
    assert report["status"] == "WARNING"
    assert report["counts"]["incomplete"] == 1
    assert report["classification_counts"] == {"INCOMPLETE_RECORD": 1}
