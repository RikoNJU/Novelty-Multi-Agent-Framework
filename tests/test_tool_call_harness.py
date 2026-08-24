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


def test_multiple_tool_calls_are_rejected_without_execution() -> None:
    tool = ExampleTool()
    response = ModelResponse(
        content=None,
        tool_calls=(
            ModelToolCall(id="call_1", name="example", arguments={"value": "1"}),
            ModelToolCall(id="call_2", name="example", arguments={"value": "2"}),
        ),
    )

    with pytest.raises(ToolCallHarnessError, match="serial harness policy") as exc:
        run_harness(
            ToolCallHarness(
                ScriptedModelClient(response), ResearcherToolRegistry([tool])
            ),
            system_prompt="system",
            initial_user_message="task",
        )

    assert tool.received == []
    assert exc.value.trace[-1].kind == "error"


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
    assert exc.value.trace[-1].detail == "tool-call budget exhausted"


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
