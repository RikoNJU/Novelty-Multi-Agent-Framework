"""Serial ToolCallHarness v1 tests with scripted model and local stub tools."""

from __future__ import annotations

import asyncio
import json

import pytest

from backend.env import ModelResponse, ModelToolCall
from novelty_agent_framework.core import (
    ToolCallHarness,
    ToolCallHarnessConfig,
    ToolCallHarnessError,
)
from novelty_agent_framework.schemas import (
    NoveltyPoint,
    ResearcherToolObservation,
    ResearchTask,
    StrictModel,
    TaskResearchRequest,
)
from novelty_agent_framework.tools import ResearcherToolRegistry
from conftest import minimal_search_plan


def scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id="paper-1",
        run_id="run-1",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="一种方法", technical_features=["特征"]
        ),
        research_task=ResearchTask(
            task_id="T-1",
            novelty_point_id="NP-1",
            task_type="search",
            language="en",
        ),
        search_plan=minimal_search_plan("T-1", "NP-1"),
    )


class ScriptedModelClient:
    def __init__(self, *responses: ModelResponse) -> None:
        self.responses = list(responses)
        self.calls = []

    async def acomplete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return self.responses.pop(0)


class ExampleArguments(StrictModel):
    value: str


class ExampleTool:
    name = "example"
    description = "Echo one value."
    args_schema = ExampleArguments

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.received: list[ExampleArguments] = []

    async def ainvoke(self, arguments, *, scope):
        self.received.append(arguments)
        if self.fail:
            raise RuntimeError("stub failed")
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            payload={"echo": arguments.value},
        )


class ReaderBudgetArguments(StrictModel):
    max_chars: int = 8000


class ReaderBudgetTool:
    name = "reader"
    description = "reader budget fixture"
    args_schema = ReaderBudgetArguments

    def __init__(self, *, actual_chars: int | None = None) -> None:
        self.actual_chars = actual_chars
        self.received: list[ReaderBudgetArguments] = []

    async def ainvoke(self, arguments, *, scope):
        self.received.append(arguments)
        actual_chars = self.actual_chars or arguments.max_chars
        return ResearcherToolObservation(
            tool_name="reader", arguments=arguments.model_dump(), succeeded=True,
            payload={"read_result": {"char_start": 0, "char_end": actual_chars}},
        )


class ProjectedExampleTool(ExampleTool):
    def project_model_context(self, observation):
        return {"succeeded": True, "handle": observation.payload["echo"]}


class DatabaseStubArguments(StrictModel):
    source_id: str = "demo"


class DatabaseStubTool:
    name = "database_search"
    description = "database stub"
    args_schema = DatabaseStubArguments

    def __init__(self, *, artifact_ids: list[str]) -> None:
        self.artifact_ids = artifact_ids
        self.received: list[DatabaseStubArguments] = []

    async def ainvoke(self, arguments, *, scope):
        self.received.append(arguments)
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            payload={
                "database_search_result": {
                    "results": [{"artifact_ids": list(self.artifact_ids)}]
                }
            },
        )


class ArtifactReaderArguments(StrictModel):
    artifact_id: str
    max_chars: int = 8_000


class ArtifactReaderStub:
    name = "reader"
    description = "artifact reader stub"
    args_schema = ArtifactReaderArguments

    def __init__(self) -> None:
        self.received: list[ArtifactReaderArguments] = []

    async def ainvoke(self, arguments, *, scope):
        self.received.append(arguments)
        return ResearcherToolObservation(
            tool_name="reader",
            arguments=arguments.model_dump(),
            succeeded=True,
            payload={
                "read_result": {"char_start": 0, "char_end": arguments.max_chars}
            },
        )


def call(arguments=None, *, call_id="call_1") -> ModelResponse:
    return ModelResponse(
        content=None,
        tool_calls=(
            ModelToolCall(
                id=call_id,
                name="example",
                arguments=arguments or {"value": "hello"},
            ),
        ),
    )


def database_call(*, call_id="call_1") -> ModelResponse:
    return ModelResponse(
        content=None,
        tool_calls=(
            ModelToolCall(
                id=call_id,
                name="database_search",
                arguments={"source_id": "demo"},
            ),
        ),
    )


def reader_call(artifact_id: str, *, call_id="call_2") -> ModelResponse:
    return ModelResponse(
        content=None,
        tool_calls=(
            ModelToolCall(
                id=call_id,
                name="reader",
                arguments={"artifact_id": artifact_id},
            ),
        ),
    )


def run_harness(harness, **kwargs):
    return asyncio.run(harness.run(scope=scope(), **kwargs))


def test_empty_registry_finishes_and_preserves_system_prompt() -> None:
    system_prompt = "immutable prompt"
    model = ScriptedModelClient(ModelResponse(content="done"))
    result = run_harness(
        ToolCallHarness(model, ResearcherToolRegistry()),
        system_prompt=system_prompt,
        initial_user_message="task",
    )

    assert result.final_content == "done"
    assert result.tool_calls_used == 0
    assert result.turns_used == 1
    assert [message.role for message in model.calls[0][0]] == ["system", "user"]
    assert model.calls[0][0][0].content == system_prompt
    assert model.calls[0][1].tools == ()


def test_registry_builds_provider_independent_tool_definitions() -> None:
    tool = ExampleTool()
    model = ScriptedModelClient(ModelResponse(content="done"))
    run_harness(
        ToolCallHarness(model, ResearcherToolRegistry([tool])),
        system_prompt="system",
        initial_user_message="task",
    )

    definitions = model.calls[0][1].tools
    assert len(definitions) == 1
    assert definitions[0].name == tool.name
    assert definitions[0].description == tool.description
    assert definitions[0].parameters == ExampleArguments.model_json_schema()


def test_one_tool_call_uses_native_trajectory_and_append_only_trace() -> None:
    tool = ExampleTool()
    model = ScriptedModelClient(
        call({"value": "original"}), ModelResponse(content="finished")
    )
    result = run_harness(
        ToolCallHarness(model, ResearcherToolRegistry([tool])),
        system_prompt="immutable prompt",
        initial_user_message="task",
    )

    assert result.final_content == "finished"
    assert result.tool_calls_used == 1
    assert tool.received[0].model_dump() == {"value": "original"}
    second_context = model.calls[1][0]
    assert [message.role for message in second_context] == [
        "system",
        "user",
        "assistant",
        "tool",
    ]
    assert second_context[2].tool_calls[0].id == "call_1"
    assert second_context[3].tool_call_id == "call_1"
    assert json.loads(second_context[3].content)["succeeded"] is True
    assert second_context[0].content == "immutable prompt"
    assert [event.kind for event in result.trace] == [
        "initial_user_message",
        "assistant_response",
        "tool_call",
        "tool_result",
        "assistant_response",
        "finish",
    ]
    assert result.trace[2].tool_call.id == result.trace[3].tool_call.id == "call_1"


def test_full_observation_is_logged_while_projection_reaches_model() -> None:
    tool = ProjectedExampleTool()
    model = ScriptedModelClient(call(), ModelResponse(content="finished"))
    result = run_harness(
        ToolCallHarness(model, ResearcherToolRegistry([tool])),
        system_prompt="system",
        initial_user_message="task",
    )

    event = next(item for item in result.trace if item.kind == "tool_result")
    assert event.observation.payload == {"echo": "hello"}
    assert json.loads(event.message.content) == {
        "succeeded": True,
        "handle": "hello",
    }


def test_multiple_tool_calls_execute_first_only() -> None:
    tool = ExampleTool()
    response = ModelResponse(
        content=None,
        tool_calls=(
            ModelToolCall(id="call_1", name="example", arguments={"value": "1"}),
            ModelToolCall(id="call_2", name="example", arguments={"value": "2"}),
        ),
    )
    result = run_harness(
        ToolCallHarness(
            ScriptedModelClient(response, ModelResponse(content="finished")),
            ResearcherToolRegistry([tool]),
        ),
        system_prompt="system",
        initial_user_message="task",
    )

    assert [item.value for item in tool.received] == ["1"]
    assert result.final_content == "finished"
    error_events = [event for event in result.trace if event.kind == "error"]
    assert error_events
    assert "multiple tool calls" in error_events[0].detail
    assert "dropped example" in error_events[0].detail


@pytest.mark.parametrize("failure", ["validation", "execution"])
def test_registry_failure_observation_is_returned_to_model(failure: str) -> None:
    tool = ExampleTool(fail=failure == "execution")
    arguments = {"wrong": "value"} if failure == "validation" else {"value": "ok"}
    model = ScriptedModelClient(call(arguments), ModelResponse(content="recovered"))

    result = run_harness(
        ToolCallHarness(model, ResearcherToolRegistry([tool])),
        system_prompt="system",
        initial_user_message="task",
    )

    tool_result = model.calls[1][0][-1]
    assert tool_result.role == "tool"
    assert tool_result.tool_call_id == "call_1"
    assert json.loads(tool_result.content)["succeeded"] is False
    assert result.final_content == "recovered"


def test_tool_call_budget_stops_repeated_requests() -> None:
    tool = ExampleTool()
    model = ScriptedModelClient(call(), call(call_id="call_2"))
    harness = ToolCallHarness(
        model,
        ResearcherToolRegistry([tool]),
        config=ToolCallHarnessConfig(max_turns=3, max_tool_calls=1),
    )

    with pytest.raises(ToolCallHarnessError, match="tool-call budget") as exc:
        run_harness(harness, system_prompt="system", initial_user_message="task")

    assert len(tool.received) == 1
    assert exc.value.trace[-1].detail == "total tool-call budget exhausted"


def test_per_tool_budget_has_distinct_runtime_error() -> None:
    tool = ExampleTool()
    model = ScriptedModelClient(call(), call(call_id="call_2"))
    harness = ToolCallHarness(
        model,
        ResearcherToolRegistry([tool]),
        config=ToolCallHarnessConfig(
            max_turns=3, max_tool_calls=3, per_tool_limits={"example": 1}
        ),
    )
    with pytest.raises(ToolCallHarnessError, match="example tool-call budget"):
        run_harness(harness, system_prompt="system", initial_user_message="task")
    assert len(tool.received) == 1


def test_reader_cumulative_character_budget_is_enforced() -> None:
    responses = (
        ModelResponse(content=None, tool_calls=(ModelToolCall("r1", "reader", {"max_chars": 6}),)),
        ModelResponse(content=None, tool_calls=(ModelToolCall("r2", "reader", {"max_chars": 5}),)),
    )
    harness = ToolCallHarness(
        ScriptedModelClient(*responses),
        ResearcherToolRegistry([ReaderBudgetTool()]),
        config=ToolCallHarnessConfig(
            max_turns=3, max_tool_calls=3, max_total_read_chars=10
        ),
    )
    with pytest.raises(ToolCallHarnessError, match="cumulative character budget"):
        run_harness(harness, system_prompt="system", initial_user_message="task")


@pytest.mark.parametrize("arguments", [{"max_chars": 1200}, {}])
def test_reader_budget_rejects_canonical_request_before_execution(arguments) -> None:
    tool = ReaderBudgetTool()
    response = ModelResponse(
        content=None,
        tool_calls=(ModelToolCall("r1", "reader", arguments),),
    )
    harness = ToolCallHarness(
        ScriptedModelClient(response),
        ResearcherToolRegistry([tool]),
        config=ToolCallHarnessConfig(max_total_read_chars=1000),
    )

    with pytest.raises(ToolCallHarnessError, match="cumulative character budget"):
        run_harness(harness, system_prompt="system", initial_user_message="task")

    assert tool.received == []


def test_reader_budget_accumulates_actual_characters() -> None:
    tool = ReaderBudgetTool(actual_chars=2500)
    responses = (
        ModelResponse(
            content=None,
            tool_calls=(ModelToolCall("r1", "reader", {"max_chars": 4000}),),
        ),
        ModelResponse(
            content=None,
            tool_calls=(ModelToolCall("r2", "reader", {"max_chars": 2500}),),
        ),
        ModelResponse(content="done"),
    )
    harness = ToolCallHarness(
        ScriptedModelClient(*responses),
        ResearcherToolRegistry([tool]),
        config=ToolCallHarnessConfig(
            max_turns=3, max_tool_calls=2, max_total_read_chars=5000
        ),
    )

    result = run_harness(harness, system_prompt="system", initial_user_message="task")

    assert result.final_content == "done"
    assert [item.max_chars for item in tool.received] == [4000, 2500]


def test_turn_budget_stops_loop_after_last_allowed_turn() -> None:
    tool = ExampleTool()
    harness = ToolCallHarness(
        ScriptedModelClient(call()),
        ResearcherToolRegistry([tool]),
        config=ToolCallHarnessConfig(max_turns=1, max_tool_calls=2),
    )

    with pytest.raises(ToolCallHarnessError, match="turn budget") as exc:
        run_harness(harness, system_prompt="system", initial_user_message="task")

    assert exc.value.trace[-1].kind == "error"


def test_model_failure_is_wrapped_with_error_trace() -> None:
    with pytest.raises(ToolCallHarnessError, match="model call failed") as exc:
        run_harness(
            ToolCallHarness(ScriptedModelClient(), ResearcherToolRegistry()),
            system_prompt="system",
            initial_user_message="task",
        )

    assert exc.value.trace[-1].kind == "error"
    assert "IndexError" in exc.value.trace[-1].detail


def test_config_rejects_non_positive_budgets() -> None:
    with pytest.raises(ValueError, match="max_turns"):
        ToolCallHarnessConfig(max_turns=0)
    with pytest.raises(ValueError, match="max_tool_calls"):
        ToolCallHarnessConfig(max_tool_calls=0)


def test_database_search_artifact_ids_require_reader_next() -> None:
    example = ExampleTool()
    database = DatabaseStubTool(artifact_ids=["a-1"])
    model = ScriptedModelClient(
        database_call(),
        call(call_id="call_2"),
        ModelResponse(content="finished"),
    )
    harness = ToolCallHarness(
        model,
        ResearcherToolRegistry([database, example]),
        config=ToolCallHarnessConfig(max_turns=4, max_tool_calls=3),
    )

    result = run_harness(
        harness, system_prompt="system", initial_user_message="task"
    )

    # 软性拒绝：example 未执行，模型收到拒绝消息后可继续
    assert len(database.received) == 1
    assert example.received == []
    assert result.final_content == "finished"
    errors = [event for event in result.trace if event.kind == "error"]
    assert errors
    assert errors[0].detail == "reader required after database_search returned artifact_ids"
    rejection = next(
        event for event in result.trace if event.kind == "tool_result"
        and event.message is not None
        and event.message.tool_call_id == "call_2"
    )
    assert json.loads(rejection.message.content)["succeeded"] is False
    assert json.loads(rejection.message.content)["required_artifact_ids"] == ["a-1"]


def test_required_reader_rejects_wrong_artifact_id() -> None:
    database = DatabaseStubTool(artifact_ids=["a-1"])
    reader = ArtifactReaderStub()
    model = ScriptedModelClient(
        database_call(),
        reader_call("a-2"),
        reader_call("a-1"),
        ModelResponse(content="finished"),
    )
    harness = ToolCallHarness(
        model,
        ResearcherToolRegistry([database, reader]),
        config=ToolCallHarnessConfig(max_turns=5, max_tool_calls=4),
    )

    result = run_harness(
        harness, system_prompt="system", initial_user_message="task"
    )

    # 错误 artifact 的 reader 调用被拒绝且不执行；正确 id 后成功读取并释放
    assert [item.artifact_id for item in reader.received] == ["a-1"]
    assert result.final_content == "finished"
    errors = [event for event in result.trace if event.kind == "error"]
    assert len(errors) == 1


def test_required_reader_accepts_artifact_id_then_releases() -> None:
    database = DatabaseStubTool(artifact_ids=["a-1"])
    reader = ArtifactReaderStub()
    example = ExampleTool()
    model = ScriptedModelClient(
        database_call(),
        reader_call("a-1"),
        call(call_id="call_3"),
        ModelResponse(content="finished"),
    )
    harness = ToolCallHarness(
        model,
        ResearcherToolRegistry([database, reader, example]),
        config=ToolCallHarnessConfig(max_turns=5, max_tool_calls=4),
    )

    result = run_harness(
        harness, system_prompt="system", initial_user_message="task"
    )

    assert result.final_content == "finished"
    assert [item.artifact_id for item in reader.received] == ["a-1"]
    assert len(example.received) == 1


def test_database_search_without_artifact_ids_imposes_no_reader_requirement() -> None:
    database = DatabaseStubTool(artifact_ids=[])
    example = ExampleTool()
    model = ScriptedModelClient(
        database_call(), call(call_id="call_2"), ModelResponse(content="finished")
    )
    harness = ToolCallHarness(
        model,
        ResearcherToolRegistry([database, example]),
        config=ToolCallHarnessConfig(max_turns=4, max_tool_calls=3),
    )

    result = run_harness(
        harness, system_prompt="system", initial_user_message="task"
    )

    assert result.final_content == "finished"
    assert len(example.received) == 1
