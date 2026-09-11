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
    ReferenceReadRequest,
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


def _read(root, artifact_id: str):
    """走 agent 层读取：命名空间由工具按制品归属自动判定。"""

    reader = ReaderTool(ReferenceArtifactReaderTool(ReferenceStore(root)))
    observation = asyncio.run(
        reader.ainvoke(
            ReaderArguments(artifact_id=artifact_id),
            scope=_scope(),
        )
    )
    return observation, observation.payload["read_result"]


def _read_explicit(root, namespace: ArtifactNamespace, artifact_id: str):
    """绕过 agent 层直接指定命名空间——底层 reader 仍然要求显式指定。"""

    reader = ReferenceArtifactReaderTool(ReferenceStore(root))
    return asyncio.run(
        reader.ainvoke(
            ReferenceReadRequest(
                subject_paper_id=PAPER_ID,
                namespace=namespace,
                artifact_id=artifact_id,
            )
        )
    )


def test_a_research_reference_reader_and_builder_baseline(tmp_path) -> None:
    research = ReferenceStore(tmp_path)
    _put(
        research,
        work_id="work_a",
        artifact_id="artifact_a",
        title="Research A",
        text="RESEARCH A QUOTE",
    )

    _observation, payload = _read(tmp_path, "artifact_a")
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

    _observation, payload = _read(tmp_path, handle.artifact_id)
    result = EvidenceCardBuilder(ReferenceStore(tmp_path)).build(
        _draft("SUBJECT B QUOTE"),
        scope=_scope(),
        read_results=[payload],
    )
    assert result.evidence_cards[0].document_title == "Subject B searchable"
    assert result.evidence[0].provenance["artifact_namespace"] == "subject_reference"


def test_c_bare_id_collision_resolves_to_research_and_stays_addressable(
    tmp_path,
) -> None:
    """同一个裸 id 同时存在于两个语料时，agent 层确定性取研究语料。

    真实数据里不会出现这种碰撞——两侧 artifact_id 的派生输入结构不同；这里只把
    平局规则固定下来，并确认自带参考语料仍可由底层 reader 显式寻址。
    """

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

    _observation, research = _read(tmp_path, "artifact_same")
    assert research["namespace"] == "research_reference"
    assert research["text"] == "RESEARCH CONTENT"

    subject = _read_explicit(
        tmp_path, ArtifactNamespace.SUBJECT_REFERENCE, "artifact_same"
    )
    assert subject.text == "SUBJECT CONTENT"
    assert subject.read_id != research["read_id"]


def test_d_subject_only_artifact_is_readable_from_the_agent_layer(tmp_path) -> None:
    """回归守卫：只存在于自带参考语料的制品，agent 层必须能读到。

    生产实测（MG19333vrw，真实模型）：模型调用 reference_search 拿到自带参考
    语料的 artifact_id，reader 的 namespace 落成默认值 research_reference，于是
    每次读取都以 ``unknown artifact_id`` 失败（同一 id 重试 4 次），既不能换一篇
    读也不能重新检索，最终预算耗尽、产出 0 张卡。根因是让模型猜制品属于哪个语料。
    """

    _put(
        SubjectReferenceStore(tmp_path),
        work_id="subject_only",
        artifact_id="artifact_x",
        title="Subject only",
        text="ONLY SUBJECT",
    )

    _observation, payload = _read(tmp_path, "artifact_x")
    assert payload["namespace"] == "subject_reference"
    assert payload["text"] == "ONLY SUBJECT"

    # 只有两个语料都不存在的 id 才允许失败
    with pytest.raises(ValueError, match="unknown artifact_id"):
        _read(tmp_path, "artifact_missing")


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
    research_observation, _payload = _read(tmp_path, "research_artifact")
    subject_observation, _payload = _read(tmp_path, "subject_artifact")
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
