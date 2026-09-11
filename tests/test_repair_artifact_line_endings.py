from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from novelty_agent_framework.persistence import ReferenceStore, paper_workspace
from novelty_agent_framework.schemas import (
    Artifact,
    ArtifactRole,
    ContentExtent,
    Work,
    WorkType,
)
from scripts.repair_artifact_line_endings import inspect_workspace


NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)
PAPER_ID = "paper-repair"
CONTENT = "line one\nline two\nline three\n"


def _artifact(artifact_id: str, work_id: str, content: str) -> Artifact:
    raw = content.encode()
    return Artifact(
        artifact_id=artifact_id,
        work_id=work_id,
        role=ArtifactRole.EXTRACTED_TEXT,
        media_type="text/plain",
        relative_path=f"documents/{work_id}/{artifact_id}.txt",
        sha256=hashlib.sha256(raw).hexdigest(),
        byte_size=len(raw),
        content_extent=ContentExtent.FULL,
        acquired_at=NOW,
    )


def _corrupted_workspace(tmp_path: Path) -> tuple[Path, Path]:
    """复现旧缺陷的产物形态：Manifest 记的是 LF 内容的 sha256，盘上却是 CRLF。"""

    paper_workspace(PAPER_ID, output_root=tmp_path)
    store = ReferenceStore(tmp_path)
    store.write_document(
        PAPER_ID,
        work_id="work-1",
        artifact_id="artifact-1",
        extension="txt",
        content=CONTENT,
    )
    store.merge_manifest(
        PAPER_ID,
        works=[Work(work_id="work-1", work_type=WorkType.ARTICLE, title="W")],
        artifacts=[_artifact("artifact-1", "work-1", CONTENT)],
    )
    path = (
        tmp_path / PAPER_ID / "references" / "documents" / "work-1" / "artifact-1.txt"
    )
    path.write_bytes(CONTENT.encode().replace(b"\n", b"\r\n"))
    return tmp_path / PAPER_ID, path


def test_dry_run_reports_repairable_without_touching_files(tmp_path) -> None:
    workspace, path = _corrupted_workspace(tmp_path)
    before = path.read_bytes()

    report = inspect_workspace(workspace)

    stats = report["namespaces"]["research"]
    assert stats["repairable"] == 1
    assert stats["ok"] == 0
    assert stats["repaired"] == 0
    assert report["repaired"] == 0
    assert path.read_bytes() == before, "dry-run 不得改写文件"


def test_apply_restores_byte_identity_and_verification(tmp_path) -> None:
    workspace, path = _corrupted_workspace(tmp_path)
    store = ReferenceStore(tmp_path)
    # 修复前：reader 读不出来
    try:
        store.verify_artifact_file(PAPER_ID, "artifact-1")
        raise AssertionError("修复前本应报 sha256 mismatch")
    except ValueError as exc:
        assert "sha256 mismatch" in str(exc)

    report = inspect_workspace(workspace, apply=True)

    assert report["repaired"] == 1
    assert report["unrepairable"] == []
    assert path.read_bytes() == CONTENT.encode(), "修复后应与 Manifest 声明的 LF 内容逐字一致"
    # 修复后：校验通过、内容照常读出
    _artifact_value, _path, raw = store.verify_artifact_file(PAPER_ID, "artifact-1")
    assert raw.decode("utf-8") == CONTENT

    # 再跑一次应当无事可做
    again = inspect_workspace(workspace, apply=True)
    assert again["repaired"] == 0
    assert again["namespaces"]["research"]["ok"] == 1


def test_content_mismatch_is_refused_not_guessed(tmp_path) -> None:
    """只有换行差异才修；内容真的对不上时必须拒绝并报出来。"""

    workspace, path = _corrupted_workspace(tmp_path)
    path.write_bytes("完全不同的一段文字\n".encode())

    report = inspect_workspace(workspace, apply=True)

    assert report["ok"] is False
    assert report["repaired"] == 0
    assert report["namespaces"]["research"]["unrepairable"] == 1
    assert report["unrepairable"][0]["artifact_id"] == "artifact-1"
    assert path.read_bytes() == "完全不同的一段文字\n".encode(), "拒绝的文件不得被改写"
