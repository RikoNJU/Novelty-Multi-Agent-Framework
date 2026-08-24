"""Provider-independent model tool-calling protocol tests."""

from __future__ import annotations

import json

import pytest

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClientError,
    ModelProfile,
    ModelToolCall,
    OpenAICompatibleChatClient,
    ToolDefinition,
)


def make_client() -> OpenAICompatibleChatClient:
    return OpenAICompatibleChatClient(
        ModelProfile(
            alias="test",
            model="test-model",
            base_url="https://example.test/v1",
            api_key="test-key",
        )
    )


class FakeHTTPResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


def mock_response(monkeypatch, message: dict) -> None:
    monkeypatch.setattr(
        "backend.env.model_client.urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeHTTPResponse(
            {"choices": [{"message": message}], "usage": {"total_tokens": 3}}
        ),
    )


def tool_call(call_id: str = "call_1", value: str = "hello") -> dict:
    return {
        "id": call_id,
        "type": "function",
        "function": {
            "name": "echo",
            "arguments": json.dumps({"value": value}),
        },
    }


def test_plain_text_response_remains_compatible(monkeypatch) -> None:
    mock_response(monkeypatch, {"role": "assistant", "content": "hello"})

    response = make_client().complete([ChatMessage(role="user", content="hi")])

    assert response.content == "hello"
    assert response.tool_calls == ()


def test_request_serializes_tool_definition_and_choice() -> None:
    definition = ToolDefinition(
        name="echo",
        description="Echo a value.",
        parameters={
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        },
    )

    payload = make_client()._build_payload(
        [ChatMessage(role="user", content="hi")],
        ModelCallOptions(tools=[definition], tool_choice="auto"),
    )

    assert payload["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Echo a value.",
                "parameters": definition.parameters,
            },
        }
    ]
    assert payload["tool_choice"] == "auto"


def test_parses_one_and_multiple_tool_calls(monkeypatch) -> None:
    mock_response(
        monkeypatch,
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [tool_call(), tool_call("call_2", "again")],
        },
    )

    response = make_client().complete([ChatMessage(role="user", content="echo")])

    assert response.content is None
    assert response.tool_calls == (
        ModelToolCall(id="call_1", name="echo", arguments={"value": "hello"}),
        ModelToolCall(id="call_2", name="echo", arguments={"value": "again"}),
    )


def test_serializes_assistant_tool_call_message() -> None:
    payload = make_client()._build_payload(
        [
            ChatMessage(
                role="assistant",
                content=None,
                tool_calls=(
                    ModelToolCall(
                        id="call_1", name="echo", arguments={"value": "你好"}
                    ),
                ),
            )
        ],
        ModelCallOptions(),
    )

    assert payload["messages"] == [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "echo",
                        "arguments": '{"value": "你好"}',
                    },
                }
            ],
        }
    ]


def test_serializes_tool_result_message() -> None:
    payload = make_client()._build_payload(
        [ChatMessage(role="tool", content="ok", tool_call_id="call_1")],
        ModelCallOptions(),
    )

    assert payload["messages"] == [
        {"role": "tool", "tool_call_id": "call_1", "content": "ok"}
    ]


@pytest.mark.parametrize("arguments", ["{not valid json", "[1, 2, 3]"])
def test_malformed_or_non_object_arguments_fail(monkeypatch, arguments: str) -> None:
    malformed = tool_call()
    malformed["function"]["arguments"] = arguments
    mock_response(
        monkeypatch,
        {"role": "assistant", "content": None, "tool_calls": [malformed]},
    )

    with pytest.raises(ModelClientError, match="arguments"):
        make_client().complete([ChatMessage(role="user", content="echo")])
