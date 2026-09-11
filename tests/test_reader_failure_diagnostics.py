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
from scripts.reader_failure_diagnostics import inspect_workspace


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
    namespace: str,
    artifact_id: str,
    message: str | None,
) -> None:
    _write(
        workspace / f"runtime/run-1/tools/{index:04d}_reader.json",
        {
            "tool_name": "reader",
            "tool_call_id": f"tool_{index:04d}",
            "stage_name": "run_research_task",
            "execution_status": "FAILED" if message else "SUCCESS",
            "agent_arguments": {"artifact_id": artifact_id},
            "resolved_arguments": {
                "namespace": namespace,
                "artifact_id": artifact_id,
                "char_start": 0,
                "max_chars": 8000,
            },
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


def test_diagnostics_classifies_each_reader_failure(tmp_path) -> None:
    report = inspect_workspace(_workspace(tmp_path))

    assert report["ok"] is True
    assert report["counts"]["reader_calls"] == 4
    assert report["counts"]["reader_failures"] == 3
    assert report["classification_counts"] == {
        "SUCCEEDED": 1,
        "WRONG_NAMESPACE": 1,
        "LOST_MANIFEST_ENTRY": 1,
        "NEVER_PERSISTED": 1,
    }


def test_diagnostics_prioritises_lost_manifest_entry_in_verdict(tmp_path) -> None:
    report = inspect_workspace(_workspace(tmp_path))

    # 悬空制品与命名空间错误同时存在时，先报更严重的丢更新
    assert "并发丢更新" in report["verdict"]
    orphan = next(
        item for item in report["failures"] if item["artifact_id"] == "art_orphan"
    )
    assert orphan["classification"] == "LOST_MANIFEST_ENTRY"
    assert orphan["error_type"] == "ValueError"


def test_diagnostics_reports_missing_runtime_records(tmp_path) -> None:
    workspace = tmp_path / "outputs" / "paper-empty"
    workspace.mkdir(parents=True)

    report = inspect_workspace(workspace)

    assert report["counts"]["reader_calls"] == 0
    assert report["classification_counts"] == {}
    assert any("runtime_debug" in item for item in report["warnings"])
