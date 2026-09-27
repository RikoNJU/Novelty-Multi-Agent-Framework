"""Exact context policy and serialized dispatch contract; no live requests."""
from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from pathlib import Path

import pytest

from backend.env import (ChatMessage, ContextAdmissionConfig, ContextTokenMeasurement,
    ModelCallOptions, ModelContextAdmissionError, ModelProfile, OpenAICompatibleChatClient,
    ToolDefinition, set_model_call_observer, reset_model_call_observer)
from backend.env.context_admission import (ContextRecordingError, count_vllm_tokens,
    evaluate_context_admission, payload_fingerprint)
from novelty_agent_framework.core import RuntimeArtifactManager, RuntimeDebugConfig


class Response:
    def __init__(self, value):
        self.value = value
        self.status = 200
        self.headers = {}
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return None
    def read(self):
        return json.dumps(self.value).encode()


def chat_response(count=60):
    return {"id": "request", "choices": [{"message": {"content": "done"}}],
            "usage": {"prompt_tokens": count, "completion_tokens": 1, "total_tokens": count + 1}}


def schema(*, tools=True):
    properties = {"model": {}, "messages": {}, "chat_template": {}, "chat_template_kwargs": {},
        "add_generation_prompt": {"default": True}, "add_special_tokens": {"default": False},
        "continue_final_message": {"default": False}}
    chat = dict(properties)
    chat["tools"] = {}
    if tools:
        properties["tools"] = {}
    return {"components": {"schemas": {"TokenizeChatRequest": {"properties": properties},
        "ChatCompletionRequest": {"properties": chat}}}}


def profile(config=None, **kwargs):
    return ModelProfile(alias="fixture", model="fixture-model", base_url="http://fixture.test:8000/v1",
        api_key="secret-fixture", context_window=100, defaults={"max_tokens": 20},
        context_admission=config or ContextAdmissionConfig(mode="enforce"), **kwargs)


def exact(count, server_window=None):
    return lambda payload: ContextTokenMeasurement(count, "fixture_exact", server_context_window=server_window)


def runtime(tmp_path):
    return RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "output", archive_root=tmp_path / "archive"))


def saved(manager):
    return json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())


def test_default_off_does_not_measure_or_change_legacy_dispatch(monkeypatch):
    dispatched = []
    def transport(request, **kwargs):
        dispatched.append(json.loads(request.data))
        return Response(chat_response())
    monkeypatch.setattr("urllib.request.urlopen", transport)
    client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig()),
        token_counter=lambda payload: pytest.fail("off must not measure"))
    response = client.complete([ChatMessage("user", "unaltered evidence")])
    assert response.content == "done"
    assert len(dispatched) == 1
    assert dispatched[0]["messages"][0]["content"] == "unaltered evidence"


@pytest.mark.parametrize("count,window,output", [(57360, 32768, 4096), (4193, 8192, 4096)])
def test_historical_context_400_counts_are_rejected_before_dispatch(monkeypatch, tmp_path, count, window, output):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("must not dispatch chat"))
    client = OpenAICompatibleChatClient(replace(profile(), context_window=32768), token_counter=exact(count, window))
    manager = runtime(tmp_path)
    manager.activate()
    try:
        with pytest.raises(ModelContextAdmissionError) as error:
            client.complete([ChatMessage("user", "fixed historical request")], options=ModelCallOptions(max_tokens=output))
    finally:
        manager.deactivate()
    assert error.value.code == "CONTEXT_LIMIT_EXCEEDED"
    record = saved(manager)
    assert record["context_admission"]["requested_total_tokens"] == count + output
    assert record["context_admission"]["effective_context_window"] == window
    assert record["error"]["code"] == "CONTEXT_LIMIT_EXCEEDED"
    assert record["chat_transport_invoked"] is False
    assert record["context_measurement_requests"] == 0
    assert record["provider_usage"] == {}
    assert "secret-fixture" not in json.dumps(record)


def test_exact_boundary_uses_completion_limit_after_all_overrides(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response(chat_response(70)))
    manager = runtime(tmp_path)
    client = OpenAICompatibleChatClient(profile(supported_params=frozenset({"max_completion_tokens"})),
        token_counter=exact(70))
    manager.activate()
    try:
        client.complete([ChatMessage("user", "evidence")], options=ModelCallOptions(
            max_tokens=99, extra_body={"max_completion_tokens": 30}))
    finally:
        manager.deactivate()
    admission = saved(manager)["context_admission"]
    assert admission["status"] == "admitted"
    assert admission["output_reservation_field"] == "max_completion_tokens"
    assert admission["requested_total_tokens"] == 100


@pytest.mark.parametrize("mode,policy,dispatch", [("observe", "reject", True),
    ("enforce", "allow", True), ("enforce", "reject", False)])
def test_unavailable_measurement_policy_is_explicit(monkeypatch, tmp_path, mode, policy, dispatch):
    calls = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: (calls.append(True) or Response(chat_response())))
    client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig(mode=mode, on_unavailable=policy)))
    manager = runtime(tmp_path)
    manager.activate()
    try:
        if dispatch:
            client.complete([ChatMessage("user", "input")])
        else:
            with pytest.raises(ModelContextAdmissionError, match="MEASUREMENT_UNAVAILABLE"):
                client.complete([ChatMessage("user", "input")])
    finally:
        manager.deactivate()
    decision = saved(manager)["context_admission"]
    assert decision["exact"] is False
    assert decision["input_tokens"] is None
    assert decision["reason"] == "no_exact_token_counter"
    assert bool(calls) == dispatch


def test_observe_exceeded_context_keeps_evidence_intact(monkeypatch, tmp_path):
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda request, **k: (requests.append(json.loads(request.data)) or Response(chat_response())))
    manager = runtime(tmp_path)
    client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig(mode="observe")), token_counter=exact(1000))
    text = "可核对引文，包含 LaTeX $\\alpha$。" * 100
    manager.activate()
    try:
        client.complete([ChatMessage("user", text)])
    finally:
        manager.deactivate()
    assert requests[0]["messages"][0]["content"] == text
    decision = saved(manager)["context_admission"]
    assert decision["status"] == "context_limit"
    assert decision["decision"] == "allow"
    assert decision["would_reject"] is True


def test_counter_mutation_cannot_change_measured_trace_or_dispatch(monkeypatch, tmp_path):
    requests = []
    def measure(payload):
        payload["messages"][0]["content"] = "mutated"
        return ContextTokenMeasurement(60, "test_exact")
    monkeypatch.setattr("urllib.request.urlopen", lambda request, **k: (requests.append(json.loads(request.data)) or Response(chat_response())))
    manager = runtime(tmp_path)
    manager.activate()
    try:
        OpenAICompatibleChatClient(profile(), token_counter=measure).complete([ChatMessage("user", "original")])
    finally:
        manager.deactivate()
    record = saved(manager)
    assert requests[0] == record["request_payload"]
    assert requests[0]["messages"][0]["content"] == "original"
    assert record["context_admission"]["payload_sha256"] == payload_fingerprint(requests[0])


@pytest.mark.parametrize("output,counter,reason", [(None, exact(2), "explicit_output_reservation_required"),
    (20, lambda p: ContextTokenMeasurement(4, "character_estimate", exact=False), "counter_is_not_exact"),
    (20, lambda p: ContextTokenMeasurement(True, "invalid"), "invalid_exact_token_count")])
def test_estimates_or_unbounded_output_are_not_claimed_exact(output, counter, reason):
    decision = evaluate_context_admission({"messages": [], "max_tokens": output},
        profile_context_window=100, config=ContextAdmissionConfig(mode="enforce"), counter=counter)
    assert decision["status"] == "measurement_unavailable"
    assert decision["reason"] == reason
    assert decision["decision"] == "reject"
    assert decision["input_tokens"] is None


def test_vllm_includes_tools_template_and_uses_server_window(monkeypatch, tmp_path):
    requests = []
    def transport(request, **kwargs):
        requests.append(request)
        if request.full_url.endswith("openapi.json"):
            return Response(schema())
        if request.full_url.endswith("tokenize"):
            return Response({"count": 60, "max_model_len": 75, "tokens": [1] * 60})
        pytest.fail("server window is smaller; chat must be refused")
    monkeypatch.setattr("urllib.request.urlopen", transport)
    manager = runtime(tmp_path)
    client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig(mode="enforce", counter="vllm"),
        supported_params=frozenset({"chat_template_kwargs"})))
    tool = ToolDefinition("reader", "read exact text", {"type": "object", "properties": {"artifact_id": {"type": "string"}}})
    manager.activate()
    try:
        with pytest.raises(ModelContextAdmissionError, match="LIMIT_EXCEEDED"):
            client.complete([ChatMessage("user", "read")], options=ModelCallOptions(tools=[tool], tool_choice="auto",
                extra_body={"chat_template_kwargs": {"enable_thinking": False}}))
    finally:
        manager.deactivate()
    token_payload = json.loads(requests[1].data)
    assert token_payload["tools"][0]["function"]["parameters"] == tool.parameters
    assert token_payload["chat_template_kwargs"] == {"enable_thinking": False}
    assert "max_tokens" not in token_payload
    assert token_payload["add_generation_prompt"] is True
    record = saved(manager)
    assert record["context_measurement_requests"] == 2
    assert record["chat_transport_invoked"] is False
    assert record["context_admission"]["effective_context_window"] == 75
    manager.finish_run("FAILED")
    totals = json.loads((manager.run_dir / "summary.json").read_text())["llm_usage"]["totals"]
    assert totals["context_measurement_requests"] == 2
    assert totals["context_pre_dispatch_rejections"] == 1
    assert totals["chat_transport_calls"] == 0


def test_vllm_085_missing_tools_field_is_not_silently_ignored(monkeypatch):
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda request, **k: (requests.append(request) or Response(schema(tools=False))))
    client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig(mode="enforce", counter="vllm")))
    with pytest.raises(ModelContextAdmissionError) as error:
        client.complete([ChatMessage("user", "read")], options=ModelCallOptions(
            tools=[ToolDefinition("reader", "read", {"type": "object"})], tool_choice="auto"))
    assert error.value.admission["reason"] == "tokenizer_missing_template_fields"
    assert error.value.admission["measurement_details"]["fields"] == ["tools"]
    assert len(requests) == 1  # schema only; no inaccurate tokenize or chat request


@pytest.mark.parametrize("token_response", [{"count": 2, "tokens": [1, 2]},
    {"count": 2, "tokens": [1], "max_model_len": 100}, {"count": -1, "tokens": [], "max_model_len": 100}])
def test_vllm_invalid_count_or_missing_window_refuses_dispatch(monkeypatch, token_response):
    monkeypatch.setattr("urllib.request.urlopen", lambda req, **k: Response(schema() if req.full_url.endswith("openapi.json") else token_response))
    client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig(mode="enforce", counter="vllm")))
    with pytest.raises(ModelContextAdmissionError, match="MEASUREMENT_UNAVAILABLE"):
        client.complete([ChatMessage("user", "text")])


def test_async_calls_share_the_same_admission_boundary(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("must not generate"))
    client = OpenAICompatibleChatClient(profile(), token_counter=exact(1000))
    with pytest.raises(ModelContextAdmissionError, match="LIMIT_EXCEEDED"):
        asyncio.run(client.acomplete([ChatMessage("user", "large context")]))


def test_admission_trace_failure_stops_even_in_observe_mode(monkeypatch):
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda request, **k: (requests.append(request) or Response(schema())))
    def observer(event):
        if event.phase == "CONTEXT_MEASUREMENT_REQUEST":
            raise OSError("trace storage unavailable")
    token = set_model_call_observer(observer)
    try:
        client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig(mode="observe", counter="vllm")))
        with pytest.raises(ContextRecordingError):
            client.complete([ChatMessage("user", "text")])
    finally:
        reset_model_call_observer(token)
    assert requests == []


def test_cancellation_during_measurement_never_starts_chat_after_cancel(monkeypatch, tmp_path):
    import threading

    measuring, release, finished = threading.Event(), threading.Event(), threading.Event()
    def counter(payload):
        measuring.set()
        release.wait(timeout=2)
        finished.set()
        return ContextTokenMeasurement(20, "blocking_exact_fixture")
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("cancelled call must not start chat"))
    client = OpenAICompatibleChatClient(profile(), token_counter=counter)
    manager = runtime(tmp_path)
    manager.activate()
    async def run():
        task = asyncio.create_task(client.acomplete([ChatMessage("user", "evidence")]))
        for _ in range(100):
            if measuring.is_set():
                break
            await asyncio.sleep(0.01)
        assert measuring.is_set()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        release.set()
        for _ in range(100):
            if finished.is_set():
                break
            await asyncio.sleep(0.01)
        await asyncio.sleep(0.05)
    try:
        asyncio.run(run())
    finally:
        release.set()
        manager.deactivate()
    record = saved(manager)
    assert record["status"] == "CANCELLED"
    assert record["chat_transport_invoked"] is False
    assert record["transport_inflight_unknown"] is False


@pytest.mark.parametrize("version", ["0.8.5", "0.8.5.post1"])
@pytest.mark.parametrize("override", [False, True])
def test_legacy_tools_mode_pins_version_and_preserves_template_precedence(monkeypatch, version, override):
    requests = []
    def transport(request, **kwargs):
        requests.append(request)
        if request.full_url.endswith("openapi.json"):
            return Response(schema(tools=False))
        if request.full_url.endswith("version"):
            return Response({"version": version})
        return Response({"count": 60, "max_model_len": 32768, "tokens": [1] * 60})
    monkeypatch.setattr("urllib.request.urlopen", transport)
    tools = [{"type": "function", "function": {"name": "reader"}}]
    payload = {"model": "fixture", "messages": [{"role": "user", "content": "text"}], "tools": tools}
    if override:
        payload["chat_template_kwargs"] = {"tools": [], "enable_thinking": False}
    measured = count_vllm_tokens(payload, base_url="http://fixture.test:8000/v1", api_key="fixture",
        config=ContextAdmissionConfig(vllm_tools_mode="v0_8_5_kwargs"))
    projected = json.loads(requests[-1].data)
    assert "tools" not in projected
    assert projected["chat_template_kwargs"]["tools"] == ([] if override else tools)
    assert payload["tools"] == tools
    assert measured.exact is True
    assert measured.details["server_version"] == version
    assert len(requests) == 3


def test_legacy_tools_mode_rejects_unverified_server_version(monkeypatch):
    requests = []
    def transport(request, **kwargs):
        requests.append(request)
        return Response(schema(tools=False) if request.full_url.endswith("openapi.json") else {"version": "0.8.6"})
    monkeypatch.setattr("urllib.request.urlopen", transport)
    client = OpenAICompatibleChatClient(profile(ContextAdmissionConfig(
        mode="enforce", counter="vllm", vllm_tools_mode="v0_8_5_kwargs")))
    with pytest.raises(ModelContextAdmissionError) as error:
        client.complete([ChatMessage("user", "text")])
    assert error.value.admission["reason"] == "legacy_tokenizer_version_not_verified"
    assert len(requests) == 2


def test_usage_mismatch_is_recorded_and_disables_next_measurement(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr("urllib.request.urlopen", lambda request, **k: (calls.append(request) or Response(chat_response(61))))
    manager = runtime(tmp_path)
    manager.activate()
    try:
        client = OpenAICompatibleChatClient(profile(), token_counter=exact(60))
        first = client.complete([ChatMessage("user", "first")])
        assert first.usage["prompt_tokens"] == 61
        with pytest.raises(ModelContextAdmissionError) as error:
            client.complete([ChatMessage("user", "second")])
    finally:
        manager.deactivate()
    assert error.value.admission["reason"] == "prior_measurement_usage_mismatch"
    records = [json.loads(p.read_text()) for p in sorted((manager.run_dir / "llm_calls").glob("*.json"))]
    assert records[0]["context_measurement_verification"]["status"] == "mismatched"
    assert records[0]["provider_usage"]["prompt_tokens"] == 61
    assert records[1]["chat_transport_invoked"] is False
    assert len(calls) == 1


def test_matching_count_is_recorded_without_invalidating_next_call(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", lambda request, **k: Response(chat_response(60)))
    manager = runtime(tmp_path)
    manager.activate()
    try:
        client = OpenAICompatibleChatClient(profile(), token_counter=exact(60))
        for _ in range(2):
            client.complete([ChatMessage("user", "text")])
    finally:
        manager.deactivate()
    records = [json.loads(p.read_text()) for p in (manager.run_dir / "llm_calls").glob("*.json")]
    assert len(records) == 2
    assert all(r["context_measurement_verification"]["status"] == "matched" for r in records)


@pytest.mark.parametrize("url", ["http://fictional-user:fictional-password@fixture.test:8000/v1",
    "http://fixture.test:8000/v1?token=fictional-secret", "http://fixture.test:8000/v1#fictional-fragment"])
def test_credentials_and_query_secrets_never_enter_admission_diagnostics(monkeypatch, tmp_path, url):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("invalid endpoint must not be called"))
    manager = runtime(tmp_path)
    manager.activate()
    try:
        client = OpenAICompatibleChatClient(replace(profile(ContextAdmissionConfig(mode="enforce", counter="vllm")), base_url=url))
        with pytest.raises(ModelContextAdmissionError) as error:
            client.complete([ChatMessage("user", "text")])
    finally:
        manager.deactivate()
    assert error.value.admission["reason"] == "model_endpoint_contains_credentials_or_query"
    record = saved(manager)
    assert "fictional-" not in json.dumps(record)
    assert record["context_measurement_requests"] == 0
