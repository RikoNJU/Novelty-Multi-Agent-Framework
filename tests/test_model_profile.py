import pytest

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClientError,
    ModelProfile,
    ModelRegistry,
    OpenAICompatibleChatClient,
)


def make_client(**profile_kwargs):
    defaults = profile_kwargs.pop(
        "defaults",
        {
            "temperature": 0.1,
            "max_tokens": 512,
            "top_p": 0.9,
            "stop": ["END"],
            "timeout_seconds": 30.0,
        },
    )
    profile = ModelProfile(
        alias="test",
        model="test-model",
        base_url="https://example.test/v1",
        api_key="test-key",
        supported_params=frozenset({"enable_thinking", "thinking_budget"}),
        defaults=defaults,
        **profile_kwargs,
    )
    return OpenAICompatibleChatClient(profile)


def test_payload_merges_profile_defaults():
    client = make_client()
    payload = client._build_payload(
        [ChatMessage(role="user", content="hello")],
        ModelCallOptions(),
    )

    assert payload["model"] == "test-model"
    assert payload["temperature"] == 0.1
    assert payload["max_tokens"] == 512
    assert payload["top_p"] == 0.9
    assert payload["stop"] == ["END"]


def test_per_call_options_override_defaults():
    client = make_client()
    payload = client._build_payload(
        [ChatMessage(role="user", content="hello")],
        ModelCallOptions(temperature=0.9, max_tokens=128, top_p=0.5),
    )

    assert payload["temperature"] == 0.9
    assert payload["max_tokens"] == 128
    assert payload["top_p"] == 0.5


def test_response_format_from_options():
    client = make_client()
    payload = client._build_payload(
        [ChatMessage(role="user", content="hello")],
        ModelCallOptions(response_format={"type": "json_object"}),
    )

    assert payload["response_format"] == {"type": "json_object"}


def test_extra_body_filtered_by_supported_params():
    client = make_client()
    payload = client._build_payload(
        [ChatMessage(role="user", content="hello")],
        ModelCallOptions(
            extra_body={
                "enable_thinking": True,
                "reasoning_effort": "max",  # 不在白名单，应被丢弃
            }
        ),
    )

    assert payload["enable_thinking"] is True
    assert "reasoning_effort" not in payload


def test_vendor_defaults_only_when_supported():
    client = make_client(
        defaults={
            "temperature": 0.2,
            "enable_thinking": False,
            "min_p": 0.1,  # 不在白名单
        }
    )
    payload = client._build_payload(
        [ChatMessage(role="user", content="hello")],
        ModelCallOptions(),
    )

    assert payload["enable_thinking"] is False
    assert "min_p" not in payload


def test_registry_builds_and_caches_clients():
    registry = ModelRegistry(
        {
            "coordinator": ModelProfile(alias="coordinator", model="glm"),
            "research": ModelProfile(alias="research", model="deepseek"),
        }
    )

    coordinator_client = registry.client_for("coordinator")
    assert coordinator_client is registry.client_for("coordinator")
    assert coordinator_client is not registry.client_for("research")
    assert registry.aliases == ("coordinator", "research")


def test_registry_unknown_alias_raises():
    registry = ModelRegistry({})
    with pytest.raises(ModelClientError):
        registry.client_for("missing")
