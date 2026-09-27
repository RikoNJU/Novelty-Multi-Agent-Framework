"""Deterministic runtime snapshots, full original history and bounded trajectories."""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import pytest

from backend.env import ChatMessage, ModelResponse, ModelToolCall
from novelty_agent_framework.core.tool_call_harness import (
    RUNTIME_STATE_PREFIX, ToolCallHarness, ToolCallHarnessConfig, ToolCallHarnessError)
from novelty_agent_framework.schemas import ResearcherToolObservation


TEXT = "Exact source quote with $x^2$ and citation [1]."


def scope(task="T-1"):
    return {"subject_paper_id": "paper", "run_id": "run", "attempt": 1,
        "novelty_point": {"point_id": "NP-1"}, "research_task": {"task_id": task}}


def call(name, **arguments):
    return ModelResponse(content=None, tool_calls=(ModelToolCall("call", name, arguments),))


def state(messages):
    rows = [message for message in messages if isinstance(message.content, str) and message.content.startswith(RUNTIME_STATE_PREFIX)]
    assert len(rows) == 1
    return json.loads(rows[0].content[len(RUNTIME_STATE_PREFIX):])


class Client:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
    async def acomplete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return self.responses.pop(0)


class Registry:
    def __init__(self):
        self.calls = []
    def descriptions(self):
        return [{"name": name, "description": name, "arguments_schema": {"type": "object"}}
                for name in ("reader", "database_search", "submit_evidence")]
    def validate_arguments(self, name, args):
        return SimpleNamespace(model_dump=lambda **_: dict(args), max_chars=args.get("max_chars", 1), reads=None)
    async def execute_validated(self, name, arguments, *, scope):
        args = arguments.model_dump()
        self.calls.append((name, args, scope))
        if name == "reader":
            start = args.get("char_start", 0)
            text = TEXT[start:start + args.get("max_chars", len(TEXT))]
            end = start + len(text)
            payload = {"read_result": {"namespace": args.get("namespace", "ns"),
                "artifact_id": args.get("artifact_id", "artifact"), "sha256": "sha",
                "read_id": f"read-{start}-{end}", "char_start": start, "char_end": end,
                "has_more": end < len(TEXT), "text": text}}
            return ResearcherToolObservation(tool_name=name, arguments=args, succeeded=True, payload=payload)
        if name == "database_search":
            failed = args.get("fail", False)
            return ResearcherToolObservation(tool_name=name, arguments=args, succeeded=not failed,
                error="Provider HTTP406; exact cause unresolved" if failed else None,
                payload={"database_search_result": {"source_id": args["source_id"], "results": []},
                    "execution_summary": {"succeeded": 0 if failed else 1, "failed": 1 if failed else 0,
                        "all_failed": failed, "provider_failed": failed}})
        return ResearcherToolObservation(tool_name=name, arguments=args, succeeded=True,
            payload={"checkpoint_id": "checkpoint", "durable": args.get("durable", True),
                "validation_stage": "builder_provenance_only", "accepted_card_ids": ["card-1"],
                "total_checkpoint_cards": 1})
    def project_model_context(self, name, observation):
        return observation.model_dump(mode="json")


def run(client, registry=None, *, config=None, task="T-1"):
    registry = registry or Registry()
    harness = ToolCallHarness(client, registry, config=config or ToolCallHarnessConfig(runtime_state_projection=True))
    result = asyncio.run(harness.run(system_prompt="original system", initial_user_message="original task", scope=scope(task)))
    return result, registry


def test_projection_replaces_one_state_without_touching_original_history():
    responses = [call("reader", artifact_id="artifact", max_chars=len(TEXT)), ModelResponse(content="done")]
    off, on = Client(responses), Client(responses)
    run(off, config=ToolCallHarnessConfig())
    run(on)
    for (old_messages, _), (new_messages, _) in zip(off.calls, on.calls, strict=True):
        state(new_messages)
        assert [m for m in new_messages if not (isinstance(m.content, str) and m.content.startswith(RUNTIME_STATE_PREFIX))] == old_messages
    assert TEXT in on.calls[-1][0][-1].content
    assert state(on.calls[-1][0])["reader_artifacts"][0]["whole_artifact_read"] is True


def test_exact_budgets_provider_failure_history_and_builder_boundary():
    client = Client([call("database_search", source_id="arxiv", fail=True),
        call("database_search", source_id="arxiv"),
        call("reader", artifact_id="artifact", max_chars=len(TEXT)), call("submit_evidence"),
        call("reader", artifact_id="artifact", char_start=len(TEXT), max_chars=1), ModelResponse(content="done")])
    config = ToolCallHarnessConfig(runtime_state_projection=True, reuse_reader_results=True,
        max_turns=10, max_tool_calls=8, max_total_read_chars=200,
        per_tool_limits={"reader": 3, "database_search": 3, "submit_evidence": 2})
    _, registry = run(client, config=config)
    snapshots = [state(messages) for messages, _ in client.calls]
    assert [s["budget"]["charged_tool_calls"] for s in snapshots] == [0, 1, 2, 3, 4, 4]
    assert [s["budget"]["remaining_exploration_calls_including_current"] for s in snapshots] == [10, 9, 8, 7, 6, 5]
    assert snapshots[-1]["budget"]["charged_read_chars"] == len(TEXT)
    assert snapshots[-1]["budget"]["remaining_read_chars"] == 200 - len(TEXT)
    assert snapshots[-1]["budget"]["remaining_per_tool"]["reader"] == 2
    provider = snapshots[-1]["providers"][0]
    assert provider["latest"]["status"] == "succeeded"
    assert provider["latest"]["successful_call_returned_zero_candidates"] is True
    assert provider["failed_tool_results"] == provider["successful_tool_results"] == 1
    assert "HTTP406" in provider["first_failure"]["error"]
    assert snapshots[1]["providers"][0]["latest"]["successful_call_returned_zero_candidates"] is False
    checkpoint = snapshots[-1]["evidence_checkpoints"][0]
    assert checkpoint["acknowledged_card_ids"] == ["card-1"]
    assert checkpoint["validation_stage"] == "builder_provenance_only"
    assert checkpoint["downstream_validator_status"] == "not_determined_by_harness"
    assert checkpoint["reviewer_status"] == "not_determined_by_harness"
    assert sum(name == "reader" for name, *_ in registry.calls) == 1


def test_long_replay_trajectory_does_not_accumulate_eof_state_or_new_read_budget():
    repeats = 30
    client = Client([call("reader", artifact_id="artifact", max_chars=len(TEXT)) for _ in range(repeats)] + [ModelResponse(content="done")])
    result, registry = run(client, config=ToolCallHarnessConfig(runtime_state_projection=True,
        reuse_reader_results=True, max_turns=32, max_tool_calls=2, max_total_read_chars=100))
    snapshots = [state(messages) for messages, _ in client.calls]
    read_states = [s["reader_artifacts"] for s in snapshots[1:]]
    assert all(value == read_states[0] for value in read_states)
    assert len(read_states[0]) == len(read_states[0][0]["read_ranges"]) == 1
    assert len(registry.calls) == 1
    assert snapshots[-1]["budget"]["charged_read_chars"] == len(TEXT)
    assert result.turns_used == 31
    # Full tool messages still grow: this is state projection, not compression.
    assert len(client.calls[-1][0]) > len(client.calls[1][0])
    assert sum(event.message.role == "tool" for event in result.trace if event.message) == repeats


def test_eof_tail_does_not_claim_unread_prefix_or_other_namespace_complete():
    client = Client([call("reader", artifact_id="same", namespace="A", char_start=10, max_chars=100),
        call("reader", artifact_id="same", namespace="B", char_start=0, max_chars=5),
        call("reader", artifact_id="same", namespace="A", char_start=0, max_chars=10), ModelResponse(content="done")])
    run(client)
    after_tail = state(client.calls[1][0])["reader_artifacts"][0]
    assert after_tail["verified_artifact_end"] == len(TEXT)
    assert after_tail["whole_artifact_read"] is False
    last = {row["namespace"]: row for row in state(client.calls[-1][0])["reader_artifacts"]}
    assert last["A"]["whole_artifact_read"] is True
    assert last["B"]["verified_artifact_end"] is None
    assert last["B"]["whole_artifact_read"] is False


def test_finalization_keeps_checkpoint_trace_and_exact_stop_budget():
    client = Client([call("reader", artifact_id="artifact", max_chars=len(TEXT)), call("submit_evidence"),
        call("reader", artifact_id="other", max_chars=1), ModelResponse(content="finished partial")])
    result, _ = run(client, config=ToolCallHarnessConfig(runtime_state_projection=True,
        finalize_on_budget=True, max_turns=6, max_tool_calls=2, max_total_read_chars=100))
    final = state(client.calls[-1][0])
    assert final["phase"] == "finalization"
    assert final["budget"]["remaining_exploration_calls_including_current"] == 0
    assert final["budget"]["remaining_tool_calls"] == 0
    assert final["budget"]["current_call_tool_execution_allowed"] is False
    assert final["evidence_checkpoints"][0]["acknowledged_card_ids"] == ["card-1"]
    assert final["stop_reason"] == result.stop_reason == "total tool-call budget exhausted"
    assert client.calls[-1][1].tools == ()
    assert any(TEXT in event.message.content for event in result.trace if event.message and event.message.content)


def test_failed_persistence_ack_is_not_projected_as_durable_card():
    client = Client([call("submit_evidence", durable=False), ModelResponse(content="done")])
    run(client)
    assert state(client.calls[-1][0])["evidence_checkpoints"] == []


def test_reader_contract_overrun_keeps_original_observation_before_budget_finish():
    class TooLong(Registry):
        async def execute_validated(self, name, arguments, *, scope):
            return await super().execute_validated(name, self.validate_arguments(name,
                {"artifact_id": "artifact", "max_chars": len(TEXT)}), scope=scope)
    client = Client([call("reader", artifact_id="artifact", max_chars=1), ModelResponse(content="partial")])
    result, _ = run(client, TooLong(), config=ToolCallHarnessConfig(runtime_state_projection=True,
        finalize_on_budget=True, max_turns=2, max_total_read_chars=1))
    final = state(client.calls[-1][0])
    assert final["budget"]["charged_read_chars"] == len(TEXT)
    assert final["budget"]["remaining_read_chars"] == 0
    assert final["reader_artifacts"][0]["whole_artifact_read"] is True
    assert any(event.observation is not None for event in result.trace)
    assert TEXT in json.dumps([event.message.content for event in result.trace if event.message])


def test_reused_harness_resets_all_task_state():
    client = Client([])
    harness = ToolCallHarness(client, Registry(), config=ToolCallHarnessConfig(runtime_state_projection=True))
    first_ids = []
    for task in ("T-1", "T-2"):
        client.responses = [call("reader", artifact_id=task, max_chars=len(TEXT)),
            call("database_search", source_id="source", fail=True), call("submit_evidence"), ModelResponse(content="done")]
        start = len(client.calls)
        asyncio.run(harness.run(system_prompt="system", initial_user_message="task", scope=scope(task)))
        snapshot = state(client.calls[start][0])
        first_ids.append(snapshot["invocation_id"])
        assert snapshot["scope"]["task_id"] == task
        assert snapshot["reader_artifacts"] == snapshot["providers"] == snapshot["evidence_checkpoints"] == []
        assert snapshot["budget"]["charged_tool_calls"] == 0
    assert len(set(first_ids)) == 2


def test_concurrent_invocations_have_separate_reader_and_budget_state():
    class Concurrent:
        def __init__(self):
            self.calls = []
            self.counts = {}
        async def acomplete(self, messages, *, options=None):
            snapshot = state(messages)
            self.calls.append(snapshot)
            task = snapshot["scope"]["task_id"]
            self.counts[task] = self.counts.get(task, 0) + 1
            await asyncio.sleep(0)
            return call("reader", artifact_id=task, max_chars=len(TEXT)) if self.counts[task] == 1 else ModelResponse(content="done")
    client = Concurrent()
    harness = ToolCallHarness(client, Registry(), config=ToolCallHarnessConfig(runtime_state_projection=True))
    async def both():
        return await asyncio.gather(*(harness.run(system_prompt="system", initial_user_message="task", scope=scope(task)) for task in ("A", "B")))
    asyncio.run(both())
    for task in ("A", "B"):
        rows = [row for row in client.calls if row["scope"]["task_id"] == task]
        assert rows[0]["reader_artifacts"] == []
        assert rows[1]["reader_artifacts"][0]["artifact_id"] == task
        assert rows[1]["budget"]["charged_tool_calls"] == 1
    assert len({row["invocation_id"] for row in client.calls}) == 2


def test_turn_limit_bounds_repetitive_models_with_full_history_preserved():
    client = Client([call("reader", artifact_id="artifact", max_chars=len(TEXT))] * 4)
    harness = ToolCallHarness(client, Registry(), config=ToolCallHarnessConfig(
        runtime_state_projection=True, reuse_reader_results=True, max_turns=4))
    with pytest.raises(ToolCallHarnessError, match="turn budget exhausted") as error:
        asyncio.run(harness.run(system_prompt="system", initial_user_message="task", scope=scope()))
    assert len(client.calls) == 4
    assert sum(event.message.role == "tool" for event in error.value.trace if event.message) == 4
    assert len(state(client.calls[-1][0])["reader_artifacts"]) == 1


def test_projected_long_input_still_passes_exact_serialized_context_admission(monkeypatch):
    from backend.env import (ContextAdmissionConfig, ContextTokenMeasurement, ModelProfile,
        OpenAICompatibleChatClient, ModelContextAdmissionError)
    from test_context_admission import Response
    measured, dispatched = [], []
    def counter(payload):
        measured.append(payload)
        # Declared deterministic transport fixture counts, not character estimates.
        return ContextTokenMeasurement(20 if len(measured) == 1 else 95, "fixture_exact")
    def transport(request, **_):
        dispatched.append(json.loads(request.data))
        return Response({"id": "fixture", "usage": {"prompt_tokens": 20,
            "completion_tokens": 1, "total_tokens": 21}, "choices": [{"message": {
                "content": None, "tool_calls": [{"id": "read", "type": "function", "function": {
                    "name": "reader", "arguments": json.dumps({"artifact_id": "artifact", "max_chars": len(TEXT)})}}]}}]})
    monkeypatch.setattr("urllib.request.urlopen", transport)
    client = OpenAICompatibleChatClient(ModelProfile(alias="fixture", model="fixture", base_url="http://fixture.test/v1",
        api_key="fixture", context_window=100, defaults={"max_tokens": 10},
        context_admission=ContextAdmissionConfig(mode="enforce")), token_counter=counter)
    harness = ToolCallHarness(client, Registry(), config=ToolCallHarnessConfig(runtime_state_projection=True))
    with pytest.raises(ToolCallHarnessError, match="model call failed") as error:
        asyncio.run(harness.run(system_prompt="system", initial_user_message="task", scope=scope()))
    assert isinstance(error.value.__cause__, ModelContextAdmissionError)
    assert len(measured) == 2 and len(dispatched) == 1
    assert measured[0] == dispatched[0]
    assert len([m for m in measured[1]["messages"] if (m.get("content") or "").startswith(RUNTIME_STATE_PREFIX)]) == 1
    assert TEXT in measured[1]["messages"][-1]["content"]
    assert any(event.observation is not None for event in error.value.trace)


def test_attempt_uses_real_research_task_scope_location():
    client = Client([ModelResponse(content="done")])
    harness = ToolCallHarness(client, Registry(), config=ToolCallHarnessConfig(runtime_state_projection=True))
    actual_shape = scope()
    actual_shape.pop("attempt")
    actual_shape["research_task"]["attempt"] = 3
    asyncio.run(harness.run(system_prompt="system", initial_user_message="task", scope=actual_shape))
    assert state(client.calls[0][0])["scope"]["attempt"] == 3
