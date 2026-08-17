import asyncio
import hashlib
import json
from datetime import datetime, timezone

import pytest

from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactRole,
    ContentExtent,
    ReferenceManifest,
    SourceKind,
    SourceRecord,
    Work,
)
from novelty_agent_framework.tools import ReferenceArtifactReaderTool
from novelty_agent_framework.schemas import ReferenceReadRequest

NOW = datetime(2026, 8, 18, tzinfo=timezone.utc)


def prepare(tmp_path, *, media_type="text/plain", content="0123456789abcdef"):
    store = ReferenceStore(tmp_path)
    work = Work(work_id="wrk_1", work_type="article", title="Paper")
    record = SourceRecord(
        source_record_id="src_1",
        work_id="wrk_1",
        source_id="test",
        source_kind=SourceKind.LOCAL,
        title="Paper",
        access_status=AccessStatus.METADATA_ONLY,
        observed_at=NOW,
    )
    extension = "txt" if media_type.startswith("text/") else "pdf"
    artifact_id = "art_1"
    store.write_document(
        "paper-1",
        work_id="wrk_1",
        artifact_id=artifact_id,
        extension=extension,
        content=content,
    )
    artifact = Artifact(
        artifact_id=artifact_id,
        work_id="wrk_1",
        source_record_id="src_1",
        role=ArtifactRole.EXTRACTED_TEXT if extension == "txt" else ArtifactRole.FULL_TEXT,
        media_type=media_type,
        relative_path=f"documents/wrk_1/{artifact_id}.{extension}",
        sha256=hashlib.sha256(content.encode()).hexdigest(),
        content_extent=ContentExtent.UNKNOWN,
        acquired_at=NOW,
    )
    store.persist_manifest(
        "paper-1",
        ReferenceManifest(
            subject_paper_id="paper-1",
            updated_at=NOW,
            works=[work],
            source_records=[record],
            artifacts=[artifact],
        ),
    )
    return store, artifact


def test_reader_returns_stable_global_slice(tmp_path):
    store, artifact = prepare(tmp_path)
    reader = ReferenceArtifactReaderTool(store)
    request = ReferenceReadRequest(
        subject_paper_id="paper-1", artifact_id=artifact.artifact_id,
        char_start=3, max_chars=5,
    )
    first = asyncio.run(reader.ainvoke(request))
    second = asyncio.run(reader.ainvoke(request))
    assert first == second
    assert first.text == "34567"
    assert (first.char_start, first.char_end, first.has_more) == (3, 8, True)


def test_reader_rejects_unknown_artifact_and_bad_offset(tmp_path):
    store, artifact = prepare(tmp_path)
    reader = ReferenceArtifactReaderTool(store)
    with pytest.raises(ValueError, match="unknown artifact_id"):
        asyncio.run(reader.ainvoke(ReferenceReadRequest(
            subject_paper_id="paper-1", artifact_id="missing"
        )))
    with pytest.raises(ValueError, match="exceeds"):
        asyncio.run(reader.ainvoke(ReferenceReadRequest(
            subject_paper_id="paper-1", artifact_id=artifact.artifact_id,
            char_start=999,
        )))


def test_reader_rejects_hash_mismatch_and_binary_media(tmp_path):
    store, artifact = prepare(tmp_path)
    path = tmp_path / "paper-1/references" / artifact.relative_path
    path.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        asyncio.run(ReferenceArtifactReaderTool(store).ainvoke(ReferenceReadRequest(
            subject_paper_id="paper-1", artifact_id=artifact.artifact_id
        )))

    binary_store, binary = prepare(tmp_path / "binary", media_type="application/pdf")
    with pytest.raises(ValueError, match="not readable text"):
        asyncio.run(ReferenceArtifactReaderTool(binary_store).ainvoke(ReferenceReadRequest(
            subject_paper_id="paper-1", artifact_id=binary.artifact_id
        )))


def test_reader_rejects_invalid_manifest_path(tmp_path):
    store, artifact = prepare(tmp_path)
    path = tmp_path / "paper-1/references/list.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["artifacts"][0]["relative_path"] = "../escape.txt"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(Exception, match="relative_path"):
        asyncio.run(ReferenceArtifactReaderTool(store).ainvoke(ReferenceReadRequest(
            subject_paper_id="paper-1", artifact_id=artifact.artifact_id
        )))


def test_reader_enforces_limit_and_sync_loop_error(tmp_path):
    store, artifact = prepare(tmp_path)
    reader = ReferenceArtifactReaderTool(store, max_chars_per_read=10)
    with pytest.raises(ValueError, match="reader limit"):
        asyncio.run(reader.ainvoke(ReferenceReadRequest(
            subject_paper_id="paper-1", artifact_id=artifact.artifact_id,
            max_chars=11,
        )))

    async def call_sync():
        with pytest.raises(RuntimeError, match="await reader.ainvoke"):
            reader.invoke(ReferenceReadRequest(
                subject_paper_id="paper-1", artifact_id=artifact.artifact_id
            ))

    asyncio.run(call_sync())
