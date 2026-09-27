"""Deterministic Reader vertical slice through the serial ToolCallHarness."""

from __future__ import annotations

import asyncio
import hashlib
import json
import pytest
from datetime import datetime, timezone

from backend.env import ModelResponse, ModelToolCall
from novelty_agent_framework.core import ToolCallHarness
from novelty_agent_framework.core.tool_call_harness import ToolCallHarnessConfig, ToolCallBudgetExhausted
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactNamespace,
    ArtifactRole,
    ContentExtent,
    NoveltyPoint,
    ReaderArguments,
    ReferenceManifest,
    ResearchTask,
    SourceKind,
    SourceRecord,
    TaskResearchRequest,
    Work,
)
from novelty_agent_framework.tools import (
    ReaderTool,
    ReferenceArtifactReaderTool,
    ResearcherToolRegistry,
)
from conftest import minimal_search_plan

PAPER_ID = "paper-test"
WORK_ID = "wrk_test"
ARTIFACT_ID = "art_test"
TEXT = (
    "Tool calling integration test document.\n"
    "The Reader must obtain this text from ReferenceStore.\n"
    "A second sentence is used to verify bounded slicing."
)
NOW = datetime(2026, 8, 25, tzinfo=timezone.utc)


class ScriptedModelClient:
    def __init__(self, *responses: ModelResponse) -> None:
        self.responses = list(responses)
        self.calls = []

    async def acomplete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return self.responses.pop(0)


def prepare_store(tmp_path) -> ReferenceStore:
    store = ReferenceStore(output_root=tmp_path)
    work = Work(work_id=WORK_ID, work_type="article", title="Harness Test Paper")
    record = SourceRecord(
        source_record_id="src_test",
        work_id=WORK_ID,
        source_id="integration-test",
        source_kind=SourceKind.LOCAL,
        title=work.title,
        access_status=AccessStatus.FULL_TEXT_ACQUIRED,
        observed_at=NOW,
    )
    store.write_document(
        PAPER_ID,
        work_id=WORK_ID,
        artifact_id=ARTIFACT_ID,
        extension="txt",
        content=TEXT,
    )
    artifact = Artifact(
        artifact_id=ARTIFACT_ID,
        work_id=WORK_ID,
        source_record_id=record.source_record_id,
        role=ArtifactRole.EXTRACTED_TEXT,
        media_type="text/plain",
        relative_path=f"documents/{WORK_ID}/{ARTIFACT_ID}.txt",
        sha256=hashlib.sha256(TEXT.encode()).hexdigest(),
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
    assert store.load_manifest(PAPER_ID).artifacts == [artifact]
    return store


def research_scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id=PAPER_ID,
        run_id="run-reader-integration",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="一种方法", technical_features=["特征"]
        ),
        research_task=ResearchTask(
            task_id="TASK-1",
            novelty_point_id="NP-1",
            task_type="read",
            language="en",
        ),
        search_plan=minimal_search_plan("TASK-1", "NP-1"),
    )


def tool_request(arguments: dict, call_id: str = "call_reader_1") -> ModelResponse:
    return ModelResponse(
        content=None,
        tool_calls=(
            ModelToolCall(
                id=call_id,
                name="reader",
                arguments=arguments,
            ),
        ),
    )


def run_reader_harness(tmp_path, arguments: dict, *, reader_limit: int = 16_000):
    store = prepare_store(tmp_path)
    reader = ReaderTool(
        ReferenceArtifactReaderTool(store, max_chars_per_read=reader_limit)
    )
    registry = ResearcherToolRegistry([reader])
    model = ScriptedModelClient(
        tool_request(arguments),
        ModelResponse(content="reader integration complete"),
    )
    result = asyncio.run(
        ToolCallHarness(model, registry).run(
            system_prompt="Use registered tools without changing this prompt.",
            initial_user_message="Read the requested artifact slice.",
            scope=research_scope(),
        )
    )
    return result, model, reader


def tool_result_payload(model: ScriptedModelClient) -> dict:
    second_context = model.calls[1][0]
    assert [message.role for message in second_context] == [
        "system",
        "user",
        "assistant",
        "tool",
    ]
    assert second_context[2].tool_calls[0].id == "call_reader_1"
    assert second_context[3].tool_call_id == "call_reader_1"
    return json.loads(second_context[3].content)


def test_real_reader_vertical_slice_exposes_definition_and_reads_store(tmp_path) -> None:
    char_start = 5
    max_chars = 17
    result, model, reader = run_reader_harness(
        tmp_path,
        {
            "artifact_id": ARTIFACT_ID,
            "char_start": char_start,
            "max_chars": max_chars,
        },
    )

    definitions = model.calls[0][1].tools
    assert len(definitions) == 1
    assert definitions[0].name == "reader"
    assert definitions[0].description == reader.description
    assert definitions[0].parameters == reader.args_schema.model_json_schema()

    payload = tool_result_payload(model)
    assert payload["succeeded"] is True
    read = payload["read_result"]
    assert read["namespace"] == ArtifactNamespace.RESEARCH_REFERENCE.value
    assert read["text"] == TEXT[char_start : char_start + max_chars]
    assert read["artifact_id"] == ARTIFACT_ID
    assert read["work_id"] == WORK_ID
    assert (read["char_start"], read["char_end"]) == (
        char_start,
        char_start + max_chars,
    )
    assert result.trace[3].observation.arguments == {
        "artifact_id": ARTIFACT_ID,
        "char_start": char_start,
        "max_chars": max_chars,
    }
    assert result.final_content == "reader integration complete"
    assert [event.kind for event in result.trace] == [
        "initial_user_message",
        "assistant_response",
        "tool_call",
        "tool_result",
        "assistant_response",
        "finish",
    ]
    tool_event = result.trace[3]
    assert tool_event.tool_call.name == "reader"
    assert tool_event.tool_call.id == "call_reader_1"
    assert tool_event.observation.succeeded is True


def test_subject_paper_id_is_rejected_as_model_argument(tmp_path) -> None:
    result, model, _reader = run_reader_harness(
        tmp_path,
        {
            "artifact_id": ARTIFACT_ID,
            "char_start": 0,
            "max_chars": 16,
            "subject_paper_id": "evil-paper",
        },
    )

    payload = tool_result_payload(model)
    assert payload["succeeded"] is False
    assert "subject_paper_id" in payload["error"]
    assert result.final_content == "reader integration complete"


def test_unknown_artifact_failure_is_returned_to_model(tmp_path) -> None:
    result, model, _reader = run_reader_harness(
        tmp_path,
        {"artifact_id": "art_missing", "char_start": 0, "max_chars": 16},
    )

    payload = tool_result_payload(model)
    assert payload["succeeded"] is False
    assert "unknown artifact_id" in payload["error"]
    assert result.trace[3].observation.succeeded is False
    assert result.final_content == "reader integration complete"


def test_reader_limit_failure_is_returned_without_harness_clamping(tmp_path) -> None:
    requested_max_chars = 17
    result, model, _reader = run_reader_harness(
        tmp_path,
        {
            "artifact_id": ARTIFACT_ID,
            "char_start": 0,
            "max_chars": requested_max_chars,
        },
        reader_limit=16,
    )

    payload = tool_result_payload(model)
    assert payload["succeeded"] is False
    assert "less than or equal to 16" in payload["error"]
    assert result.trace[3].observation.arguments["max_chars"] == requested_max_chars
    assert result.trace[3].tool_call.arguments["max_chars"] == requested_max_chars
    assert result.final_content == "reader integration complete"


def test_batch_reads_keep_successful_slices_on_individual_failure(tmp_path):
    from novelty_agent_framework.workflows.research_task import _trusted_reads

    result, model, _ = run_reader_harness(tmp_path, {"reads": [
        {"artifact_id": ARTIFACT_ID, "max_chars": 10},
        {"artifact_id": "missing", "max_chars": 10},
        {"artifact_id": ARTIFACT_ID, "char_start": 20, "max_chars": 15},
    ]})
    payload = tool_result_payload(model)
    assert [row["text"] for row in payload["read_results"]] == [TEXT[:10], TEXT[20:35]]
    assert payload["read_errors"][0]["index"] == 1
    reads, warnings = _trusted_reads(result.trace)
    assert not warnings
    assert len(reads) == 2
    assert len({read.read_id for read in reads}) == 2


@pytest.mark.parametrize("budget,followup", [(19, False), (29, True), (30, True)])
def test_batch_reader_sums_requested_and_actual_character_budgets(tmp_path, budget, followup):
    reader = ReaderTool(ReferenceArtifactReaderTool(prepare_store(tmp_path)))
    responses = [tool_request({"reads": [
        {"artifact_id": ARTIFACT_ID, "max_chars": 10},
        {"artifact_id": ARTIFACT_ID, "char_start": 20, "max_chars": 10},
    ]})]
    if followup:
        responses.append(tool_request({"artifact_id": ARTIFACT_ID, "max_chars": 10}, "r2"))
    responses.append(ModelResponse(content="done"))
    harness = ToolCallHarness(ScriptedModelClient(*responses), ResearcherToolRegistry([reader]),
                              config=ToolCallHarnessConfig(max_total_read_chars=budget))
    async def run():
        return await harness.run(system_prompt="test", initial_user_message="test", scope=research_scope())
    if budget < 30:
        with pytest.raises(ToolCallBudgetExhausted, match="character budget"):
            asyncio.run(run())
    else:
        assert asyncio.run(run()).final_content == "done"


def test_batch_default_limits_and_exclusive_modes(tmp_path):
    from pydantic import ValidationError
    reader = ReaderTool(ReferenceArtifactReaderTool(prepare_store(tmp_path), max_chars_per_read=200),
                        default_chars_per_read=100)
    args = reader.args_schema.model_validate({"reads": [{"artifact_id": ARTIFACT_ID}]})
    assert args.reads[0].max_chars == 100
    for invalid in ({}, {"reads": []}, {"artifact_id": ARTIFACT_ID, "reads": [{"artifact_id": ARTIFACT_ID}]},
                    {"reads": [{"artifact_id": ARTIFACT_ID}] * 5},
                    {"reads": [{"artifact_id": ARTIFACT_ID, "max_chars": 201}]},
                    {"reads": [{"artifact_id": ARTIFACT_ID}], "max_chars": 1}):
        with pytest.raises(ValidationError):
            reader.args_schema.model_validate(invalid)


@pytest.mark.parametrize("enabled,physical_reads", [(False, 2), (True, 1)])
def test_exact_reader_replay_keeps_provenance_without_new_reads(tmp_path, enabled, physical_reads):
    from novelty_agent_framework.workflows.research_task import _trusted_reads

    low_level = ReferenceArtifactReaderTool(prepare_store(tmp_path))
    original = low_level.ainvoke
    dispatched = []

    async def counted(request):
        dispatched.append(request)
        return await original(request)

    low_level.ainvoke = counted
    args = {"artifact_id": ARTIFACT_ID, "max_chars": 16}
    model = ScriptedModelClient(tool_request(args, "first"), tool_request(args, "again"),
                                ModelResponse(content="done"))
    result = asyncio.run(ToolCallHarness(model, ResearcherToolRegistry([ReaderTool(low_level)]),
        config=ToolCallHarnessConfig(reuse_reader_results=enabled)).run(
            system_prompt="test", initial_user_message="test", scope=research_scope()))
    assert len(dispatched) == physical_reads
    assert result.tool_calls_used == physical_reads
    payloads = [json.loads(e.message.content) for e in result.trace if e.kind == "tool_result"]
    assert payloads[0]["read_result"] == payloads[1]["read_result"]
    assert payloads[1].get("reused_result", False) == enabled
    reads, warnings = _trusted_reads(result.trace)
    assert not warnings
    assert len(reads) == physical_reads
    assert reads[0].text == TEXT[:16]
    assert len({r.read_id for r in reads}) == 1


def test_reader_replay_remains_available_after_execution_and_character_budget(tmp_path):
    model = ScriptedModelClient(tool_request({"artifact_id": ARTIFACT_ID, "max_chars": 16}, "first"),
        tool_request({"artifact_id": ARTIFACT_ID, "max_chars": 16}, "again"), ModelResponse(content="done"))
    result = asyncio.run(ToolCallHarness(model, ResearcherToolRegistry([
        ReaderTool(ReferenceArtifactReaderTool(prepare_store(tmp_path)))]),
        config=ToolCallHarnessConfig(reuse_reader_results=True, max_tool_calls=1,
            per_tool_limits={"reader": 1}, max_total_read_chars=16)).run(
                system_prompt="test", initial_user_message="test", scope=research_scope()))
    assert result.tool_calls_used == 1
    assert result.turns_used == 3
    assert result.final_content == "done"


def test_reader_eof_guard_preserves_unread_prefix_and_changed_ranges(tmp_path):
    from novelty_agent_framework.workflows.research_task import _trusted_reads

    requests = [
        {"artifact_id": ARTIFACT_ID, "char_start": len(TEXT) - 10, "max_chars": 16},
        {"artifact_id": ARTIFACT_ID, "char_start": len(TEXT), "max_chars": 16},
        {"artifact_id": ARTIFACT_ID, "char_start": len(TEXT) + 10, "max_chars": 16},
        {"artifact_id": ARTIFACT_ID, "char_start": 0, "max_chars": 16},
        {"artifact_id": ARTIFACT_ID, "char_start": 8, "max_chars": 16},
    ]
    model = ScriptedModelClient(*(tool_request(args, f"r{i}") for i, args in enumerate(requests)),
                                ModelResponse(content="done"))
    result = asyncio.run(ToolCallHarness(model, ResearcherToolRegistry([
        ReaderTool(ReferenceArtifactReaderTool(prepare_store(tmp_path)))]),
        config=ToolCallHarnessConfig(reuse_reader_results=True)).run(
            system_prompt="test", initial_user_message="test", scope=research_scope()))
    assert result.tool_calls_used == 3
    replayed = [e for e in result.trace if e.detail == "reader_state_reused"]
    assert len(replayed) == 2
    assert all(json.loads(e.message.content)["read_status"] == "artifact_eof" for e in replayed)
    reads, warnings = _trusted_reads(result.trace)
    assert not warnings
    assert [r.text for r in reads] == [TEXT[-10:], TEXT[:16], TEXT[8:24]]
    assert "Reader state" in model.calls[-1][0][0].content


def test_reader_cache_is_invocation_scoped_and_failed_reads_are_not_cached(tmp_path):
    low_level = ReferenceArtifactReaderTool(prepare_store(tmp_path))
    original = low_level.ainvoke
    dispatched = []

    async def counted(request):
        dispatched.append(request)
        if len(dispatched) == 1:
            raise OSError("transient local read failure")
        return await original(request)

    low_level.ainvoke = counted
    model = ScriptedModelClient()
    harness = ToolCallHarness(model, ResearcherToolRegistry([ReaderTool(low_level)]),
        config=ToolCallHarnessConfig(reuse_reader_results=True))
    for _ in range(2):
        model.responses = [tool_request({"artifact_id": ARTIFACT_ID, "max_chars": 16}, "first"),
            tool_request({"artifact_id": ARTIFACT_ID, "max_chars": 16}, "again"), ModelResponse(content="done")]
        asyncio.run(harness.run(system_prompt="test", initial_user_message="test", scope=research_scope()))
    assert len(dispatched) == 3  # first failure + successful retry + new invocation


def test_reader_repetition_is_still_bounded_by_model_turn_budget(tmp_path):
    args = {"artifact_id": ARTIFACT_ID, "max_chars": 16}
    model = ScriptedModelClient(*(tool_request(args, f"repeat-{i}") for i in range(3)))
    harness = ToolCallHarness(model, ResearcherToolRegistry([
        ReaderTool(ReferenceArtifactReaderTool(prepare_store(tmp_path)))]),
        config=ToolCallHarnessConfig(reuse_reader_results=True, max_turns=3))
    with pytest.raises(ToolCallBudgetExhausted, match="turn budget") as error:
        asyncio.run(harness.run(system_prompt="test", initial_user_message="test", scope=research_scope()))
    assert len(model.calls) == 3
    assert sum(e.kind == "tool_call" for e in error.value.trace) == 1
    assert sum(e.detail == "reader_state_reused" for e in error.value.trace) == 2


def test_batch_replay_preserves_all_handles_and_mixed_eof_batch_is_not_dropped(tmp_path):
    from novelty_agent_framework.workflows.research_task import _trusted_reads

    full = {"artifact_id": ARTIFACT_ID, "max_chars": len(TEXT)}
    mixed = {"reads": [{"artifact_id": ARTIFACT_ID, "char_start": len(TEXT), "max_chars": 16},
                       {"artifact_id": ARTIFACT_ID, "char_start": 5, "max_chars": 16}]}
    model = ScriptedModelClient(tool_request(full, "full"), tool_request(mixed, "mixed"),
        tool_request(mixed, "mixed-again"), ModelResponse(content="done"))
    result = asyncio.run(ToolCallHarness(model, ResearcherToolRegistry([
        ReaderTool(ReferenceArtifactReaderTool(prepare_store(tmp_path)))]),
        config=ToolCallHarnessConfig(reuse_reader_results=True)).run(
            system_prompt="test", initial_user_message="test", scope=research_scope()))
    assert result.tool_calls_used == 2
    reads, warnings = _trusted_reads(result.trace)
    assert not warnings
    assert [r.text for r in reads] == [TEXT, "", TEXT[5:21]]
    assert result.trace[-3].detail == "reader_state_reused"


def test_reader_state_never_shares_eof_across_namespaces():
    from novelty_agent_framework.core.tool_call_harness import _ReaderState
    from novelty_agent_framework.schemas import ResearcherToolObservation

    state = _ReaderState()
    def remember(namespace):
        row = {"namespace": namespace, "artifact_id": "same", "read_id": "same-read",
               "sha256": namespace, "char_start": 0, "char_end": 3, "text": "abc", "has_more": False}
        arguments = {"namespace": namespace, "artifact_id": "same", "char_start": 0, "max_chars": 3}
        state.remember(arguments, ResearcherToolObservation(tool_name="reader", succeeded=True,
            arguments=arguments, payload={"read_result": row}), {"read_result": row})

    remember("research_reference")
    assert state.replay({"namespace": "research_reference", "artifact_id": "same", "char_start": 3})
    assert state.replay({"namespace": "subject_reference", "artifact_id": "same", "char_start": 3}) is None
    remember("subject_reference")
    assert len(state.reads) == 2
    assert state.replay({"artifact_id": "same", "char_start": 3}) is None


@pytest.mark.parametrize("eof,remaining", [(False, ["other"]), (True, [ARTIFACT_ID, "other"])])
def test_reader_replay_only_discharges_nonempty_matching_mandatory_reads(tmp_path, eof, remaining):
    from novelty_agent_framework.schemas import StrictModel, ResearcherToolObservation

    class Arguments(StrictModel):
        pass
    class Database:
        name = "database_search"
        description = "fixed fixture"
        args_schema = Arguments
        async def ainvoke(self, arguments, *, scope):
            return ResearcherToolObservation(tool_name=self.name, succeeded=True,
                payload={"database_search_result": {"results": [{"artifact_ids": [ARTIFACT_ID, "other"]}]}})
    def db(name):
        return ModelResponse(content=None, tool_calls=(ModelToolCall(name, "database_search", {}),))

    first = {"artifact_id": ARTIFACT_ID, "max_chars": len(TEXT)}
    replay = {"artifact_id": ARTIFACT_ID, "char_start": len(TEXT), "max_chars": 16} if eof else first
    model = ScriptedModelClient(tool_request(first), db("db1"), tool_request(replay, "again"),
                                db("db2"), tool_request(first, "unrelated"), db("db3"), ModelResponse(content="done"))
    result = asyncio.run(ToolCallHarness(model, ResearcherToolRegistry([
        ReaderTool(ReferenceArtifactReaderTool(prepare_store(tmp_path))), Database()]),
        config=ToolCallHarnessConfig(reuse_reader_results=True)).run(
            system_prompt="test", initial_user_message="test", scope=research_scope()))
    results = [json.loads(e.message.content) for e in result.trace if e.kind == "tool_result"]
    assert results[3]["required_artifact_ids"] == sorted(remaining)
    assert results[-1]["required_artifact_ids"] == ["other"]
    if not eof:
        assert results[-2]["required_artifact_ids"] == ["other"]
