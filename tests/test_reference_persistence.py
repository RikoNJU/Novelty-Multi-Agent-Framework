import hashlib
import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

import novelty_agent_framework.persistence as persistence
from novelty_agent_framework.persistence import (
    ReferenceStore,
    load_reference_manifest,
    merge_record,
    paper_workspace,
    persist_reference_manifest,
    reference_documents_dir,
    reference_workspace,
)
from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactRole,
    ContentExtent,
    ReferenceManifest,
    SourceKind,
    SourceRecord,
    Work,
    WorkType,
)


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


def test_write_document_is_byte_exact_so_declared_sha256_verifies(tmp_path):
    """回归守卫：文本模式写入曾在 Windows 上把 ``\\n`` 翻译成 ``\\r\\n``。

    落盘字节与调用方计算 sha256 时所用的 ``content.encode()`` 不一致，
    ``verify_artifact_file`` 因而抛 sha256 mismatch，完整性门会拒绝所有卡片。
    """

    store = ReferenceStore(tmp_path)
    content = "first line\nsecond line\n"
    path = store.write_document(
        "paper-1",
        work_id="work-1",
        artifact_id="artifact-1",
        extension="txt",
        content=content,
    )
    assert path.read_bytes() == content.encode("utf-8")
    assert b"\r\n" not in path.read_bytes()

    manifest = store.load_manifest("paper-1")
    store.persist_manifest(
        "paper-1",
        manifest.model_copy(
            update={
                "works": [
                    Work(work_id="work-1", work_type=WorkType.ARTICLE, title="Work 1")
                ],
                "artifacts": [
                    Artifact(
                        artifact_id="artifact-1",
                        work_id="work-1",
                        role=ArtifactRole.EXTRACTED_TEXT,
                        media_type="text/plain",
                        relative_path="documents/work-1/artifact-1.txt",
                        sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                        byte_size=len(content.encode("utf-8")),
                        content_extent=ContentExtent.FULL,
                        acquired_at=datetime(2026, 9, 11, tzinfo=timezone.utc),
                    )
                ],
            }
        ),
    )

    _artifact, _path, raw = store.verify_artifact_file("paper-1", "artifact-1")
    assert raw == content.encode("utf-8")


def test_persisted_text_uses_lf_line_endings(tmp_path):
    """仓库会提交这些产物，固定 LF 才能保证跨平台 diff 与哈希稳定。"""

    manifest = ReferenceManifest(
        subject_paper_id="paper-1",
        updated_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
    )
    path = persist_reference_manifest("paper-1", manifest, output_root=tmp_path)
    raw = path.read_bytes()
    assert b"\r\n" not in raw
    assert raw.endswith(b"\n")


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
        acquired_at=datetime(2026, 9, 11, tzinfo=timezone.utc),
    )


def _work(work_id: str) -> Work:
    return Work(work_id=work_id, work_type=WorkType.ARTICLE, title=work_id)


def test_merge_manifest_keeps_entries_from_concurrent_writers(tmp_path):
    """回归守卫：manifest 是「读-改-写」共享状态，必须合并而不是整份覆盖。

    structured_retrieval / browser 在 load_manifest 与 persist_manifest 之间
    有多次 await，6 个 Researcher 任务并行时会各自基于旧副本整份写回，后写者
    抹掉先写者的条目——正文文件仍在磁盘上，但清单里没有记录，reader 随即报
    unknown artifact_id（实测表现为同一个 id 反复读取失败）。
    """

    paper_workspace("paper-1", output_root=tmp_path)
    store = ReferenceStore(tmp_path)

    store.merge_manifest(
        "paper-1",
        works=[_work("work-a")],
        artifacts=[_artifact("art_a", "work-a", "A")],
    )
    store.merge_manifest(
        "paper-1",
        works=[_work("work-b")],
        artifacts=[_artifact("art_b", "work-b", "B")],
    )

    manifest = store.load_manifest("paper-1")
    assert {item.artifact_id for item in manifest.artifacts} == {"art_a", "art_b"}
    assert {item.work_id for item in manifest.works} == {"work-a", "work-b"}


def test_merge_record_allows_late_work_id_binding(tmp_path):
    """Browser 会先写入记录、之后才补上 work_id；这不算身份冲突。"""

    source = SourceRecord(
        source_record_id="rec-1",
        work_id=None,
        source_id="demo",
        source_kind=SourceKind.WEB,
        title="Rec",
        access_status=AccessStatus.METADATA_ONLY,
        observed_at=datetime(2026, 9, 11, tzinfo=timezone.utc),
    )
    bound = source.model_copy(update={"work_id": "work-1"})

    target: dict = {}
    merge_record(target, source)
    merge_record(target, bound)

    assert target["rec-1"].work_id == "work-1"
