from __future__ import annotations

import json
import asyncio
import threading
from datetime import datetime, timezone
from pathlib import Path

from backend.env import (ChatMessage, ModelCallBudgetExceeded, ModelCallEvent, ModelProfile, ModelResponse, ModelTraceError, ModelTransportTimeout,
                         OpenAICompatibleChatClient, reset_model_call_observer,
                         set_model_call_observer)
from novelty_agent_framework.core import RuntimeArtifactManager, RuntimeDebugConfig
from novelty_agent_framework.diagnostics.llm_usage import LlmPricingCatalog


class _FakeHTTPResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return json.dumps(
            {
                "id": "request-1",
                "choices": [{"message": {"role": "assistant", "content": "ok"}}],
                "usage": {
                    "prompt_tokens": 1000,
                    "completion_tokens": 500,
                    "total_tokens": 1500,
                    "prompt_tokens_details": {"cached_tokens": 200},
                    "completion_tokens_details": {"reasoning_tokens": 100},
                },
            }
        ).encode()


def test_pricing_uses_cached_and_off_peak_rates() -> None:
    catalog = LlmPricingCatalog.load()
    result = catalog.calculate(
        "deepseek-ai/DeepSeek-V4-Flash",
        {
            "prompt_tokens": 1000,
            "completion_tokens": 500,
            "total_tokens": 1500,
            "prompt_tokens_details": {"cached_tokens": 200},
        },
        occurred_at=datetime(2026, 9, 6, 19, 0, tzinfo=timezone.utc),
    )

    assert result["billing"]["status"] == "PRICED"
    assert result["billing"]["rate_name"] == "off_peak_02_08"
    assert result["billing"]["amount"] == 0.00348
    assert result["tokens"]["cached_input_tokens"] == 200


def test_unknown_model_tracks_tokens_without_claiming_zero_cost() -> None:
    catalog = LlmPricingCatalog.load()
    result = catalog.calculate(
        "vendor/unknown",
        {"prompt_tokens": 7, "completion_tokens": 3},
        occurred_at=datetime.now(timezone.utc),
    )

    assert result["tokens"]["total_tokens"] == 10
    assert result["billing"]["status"] == "UNPRICED"
    assert result["billing"]["amount"] is None


def test_total_only_usage_is_not_misreported_as_free() -> None:
    catalog = LlmPricingCatalog.load()
    result = catalog.calculate(
        "deepseek-ai/DeepSeek-V4-Flash",
        {"total_tokens": 10},
        occurred_at=datetime.now(timezone.utc),
    )

    assert result["tokens"]["total_tokens"] == 10
    assert result["billing"]["status"] == "USAGE_INCOMPLETE"
    assert result["billing"]["amount"] is None


def test_client_call_is_persisted_and_aggregated(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "backend.env.model_client.urllib.request.urlopen",
        lambda *_args, **_kwargs: _FakeHTTPResponse(),
    )
    manager = RuntimeArtifactManager(
        "paper",
        config=RuntimeDebugConfig(
            output_root=tmp_path / "outputs",
            archive_root=tmp_path / "archive",
        ),
    )
    client = OpenAICompatibleChatClient(
        ModelProfile(
            alias="deepseek-flash",
            provider="openai_compatible",
            model="deepseek-ai/DeepSeek-V4-Flash",
            base_url="https://example.test/v1",
            api_key="test-key",
        )
    )

    manager.activate()
    stage = manager.start_stage("coordinator", {})
    client.complete([ChatMessage(role="user", content="hello")])
    manager.finish_stage(stage, {})
    manager.finish_run("SUCCESS")
    manager.deactivate()

    call = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text(encoding="utf-8"))
    assert call["llm_call_id"] == "llm_0001"
    assert call["stage_name"] == "coordinator"
    assert call["request_id"] == "request-1"
    assert call["request_payload"]["messages"] == [{"role": "user", "content": "hello"}]
    assert call["request_payload"]["model"] == "deepseek-ai/DeepSeek-V4-Flash"
    assert call["request_options"]["timeout_seconds"] == 60.0
    assert call["response"]["content"] == "ok"
    assert "test-key" not in json.dumps(call)
    assert call["tokens"]["total_tokens"] == 1500
    assert call["billing"]["currency"] == "RMB"
    assert call["billing"]["amount"] is not None

    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    totals = summary["llm_usage"]["totals"]
    assert totals["calls"] == 1
    assert totals["input_tokens"] == 1000
    assert totals["cached_input_tokens"] == 200
    assert totals["output_tokens"] == 500
    assert totals["reasoning_tokens"] == 100
    assert totals["amount_rmb"] > 0
    assert "## LLM Token Usage and Cost" in (manager.run_dir / "summary.md").read_text(encoding="utf-8")


def test_failed_model_call_keeps_request_and_terminal_error(monkeypatch, tmp_path: Path) -> None:
    import pytest

    def fail(*_args, **_kwargs):
        raise OSError("offline")

    monkeypatch.setattr("backend.env.model_client.urllib.request.urlopen", fail)
    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive"))
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="test-key"))
    manager.activate()
    with pytest.raises(Exception, match="offline"):
        client.complete([ChatMessage(role="user", content="saved request")])
    manager.deactivate()
    call = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
    assert call["status"] == "FAILED"
    assert call["request_payload"]["messages"][0]["content"] == "saved request"
    assert call["error"]["type"] == "ModelClientError"


def test_trace_switch_preserves_request_and_response(monkeypatch, tmp_path: Path) -> None:
    requests: list[bytes] = []

    def fake(request, **_kwargs):
        requests.append(request.data)
        return _FakeHTTPResponse()

    monkeypatch.setattr("backend.env.model_client.urllib.request.urlopen", fake)
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="test-key"))
    outputs = []
    for enabled in (False, True):
        manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
            enabled=enabled, output_root=tmp_path / f"outputs-{enabled}",
            archive_root=tmp_path / f"archive-{enabled}"))
        manager.activate()
        outputs.append(client.complete([ChatMessage(role="user", content="same")]))
        manager.deactivate()
    assert requests[0] == requests[1]
    assert outputs[0] == outputs[1]


def test_interrupted_sync_model_call_has_terminal_trace(tmp_path: Path) -> None:
    import pytest

    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive"))
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="stub"))

    def interrupt(*_args, **_kwargs):
        raise KeyboardInterrupt()

    client._complete = interrupt
    manager.activate()
    with pytest.raises(KeyboardInterrupt):
        client.complete([ChatMessage(role="user", content="input")])
    manager.deactivate()
    call = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
    assert call["status"] == "CANCELLED"
    assert call["transport_inflight_unknown"] is False
    assert call["request_payload"]["messages"][0]["content"] == "input"


def test_trace_failure_stops_before_model_request() -> None:
    import pytest

    calls = []
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="stub"))
    client._complete = lambda *_args, **_kwargs: calls.append(True)

    def broken(_event):
        raise OSError("disk unavailable")

    token = set_model_call_observer(broken)
    try:
        with pytest.raises(ModelTraceError, match="trace_incomplete"):
            client.complete([ChatMessage(role="user", content="input")])
    finally:
        reset_model_call_observer(token)
    assert calls == []


def test_model_call_cap_stops_before_second_dispatch(monkeypatch, tmp_path: Path) -> None:
    import pytest

    dispatched = []

    def fake_urlopen(*_args, **_kwargs):
        dispatched.append(True)
        return _FakeHTTPResponse()

    monkeypatch.setattr("backend.env.model_client.urllib.request.urlopen", fake_urlopen)
    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive",
        max_model_calls=1))
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="stub"))
    manager.activate()
    try:
        client.complete([ChatMessage(role="user", content="first")])
        with pytest.raises(ModelCallBudgetExceeded, match="model_call_budget_exhausted"):
            client.complete([ChatMessage(role="user", content="second")])
    finally:
        manager.deactivate()
    assert dispatched == [True]
    assert len(list((manager.run_dir / "llm_calls").glob("*.json"))) == 1


def test_cancelled_async_model_call_retains_terminal_trace(tmp_path: Path) -> None:
    import pytest

    started = threading.Event()
    release = threading.Event()
    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive"))
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="stub"))

    def blocked(*_args, **_kwargs):
        started.set()
        release.wait(timeout=2)
        return ModelResponse(content="late")

    client._complete = blocked
    manager.activate()

    async def cancel_call() -> None:
        task = asyncio.create_task(client.acomplete([ChatMessage(role="user", content="input")]))
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.01)
        assert started.is_set()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        release.set()
        await asyncio.sleep(0.05)

    asyncio.run(cancel_call())
    manager.deactivate()
    call = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
    assert call["status"] == "CANCELLED"
    assert call["request_payload"]["messages"][0]["content"] == "input"


def test_late_transport_completion_is_recorded_without_reviving_cancelled_run(monkeypatch, tmp_path: Path) -> None:
    started = threading.Event()
    release = threading.Event()

    class SlowResponse(_FakeHTTPResponse):
        status = 200
        headers = {"x-request-id": "late-request"}

        def read(self):
            started.set()
            release.wait(timeout=2)
            return super().read()

    monkeypatch.setattr("backend.env.model_client.urllib.request.urlopen",
                        lambda *_args, **_kwargs: SlowResponse())
    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive"))
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="stub"))
    manager.activate()

    async def cancel_then_release():
        task = asyncio.create_task(client.acomplete([ChatMessage(role="user", content="input")]))
        try:
            for _ in range(100):
                if started.is_set() or task.done():
                    break
                await asyncio.sleep(0.01)
            if task.done():
                await task  # Surface an observer or transport failure immediately.
            assert started.is_set()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            cancelled = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
            assert cancelled["transport_inflight_unknown"] is True
            manager.finish_run("FAILED")
            release.set()
            for _ in range(50):
                call = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
                if call.get("late_completion"):
                    return call
                await asyncio.sleep(0.01)
            raise AssertionError("late transport completion was not recorded")
        finally:
            release.set()

    try:
        call = asyncio.run(cancel_then_release())
    finally:
        release.set()
        manager.deactivate()
    assert call["status"] == "CANCELLED"
    assert call["late_completion"]["status"] == "SUCCESS"
    assert call["transport_inflight_unknown"] is False
    assert call["late_completion"]["response_id"] == "request-1"
    phases = [item["phase"] for item in call["timeline"]]
    assert phases == ["TRANSPORT_INVOKED", "RESPONSE_HEADERS",
                      "RESPONSE_BODY_COMPLETE", "RESPONSE_PARSED"]
    archived = next((tmp_path / "archive").glob("**/llm_calls/*.json"))
    import time
    for _ in range(50):
        if json.loads(archived.read_text()).get("late_completion"):
            break
        time.sleep(0.01)
    assert json.loads(archived.read_text())["late_completion"] == call["late_completion"]


def test_transport_headers_delay_and_http_failure_have_distinct_traces(monkeypatch, tmp_path: Path) -> None:
    import urllib.error

    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive"))
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="test", provider="openai_compatible", model="test-model",
        base_url="https://example.test/v1", api_key="stub"))

    def delayed_headers(*_args, **_kwargs):
        import time
        time.sleep(0.02)
        return _FakeHTTPResponse()

    monkeypatch.setattr("backend.env.model_client.urllib.request.urlopen", delayed_headers)
    manager.activate()
    try:
        client.complete([ChatMessage(role="user", content="input")])
    finally:
        manager.deactivate()
    call = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
    assert call["status"] == "SUCCESS"
    assert [item["phase"] for item in call["timeline"]] == [
        "TRANSPORT_INVOKED", "RESPONSE_HEADERS", "RESPONSE_BODY_COMPLETE", "RESPONSE_PARSED"]
    assert call["timeline"][1]["at"] >= call["timeline"][0]["at"]

    manager2 = RuntimeArtifactManager("paper2", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs2", archive_root=tmp_path / "archive2"))

    def http_error(*_args, **_kwargs):
        raise urllib.error.HTTPError("https://example.test", 503, "unavailable", {}, None)

    monkeypatch.setattr("backend.env.model_client.urllib.request.urlopen", http_error)
    manager2.activate()
    try:
        import pytest
        with pytest.raises(Exception, match="503"):
            client.complete([ChatMessage(role="user", content="input")])
    finally:
        manager2.deactivate()
    failed = json.loads(next((manager2.run_dir / "llm_calls").glob("*.json")).read_text())
    assert failed["status"] == "FAILED"
    assert [item["phase"] for item in failed["timeline"]] == ["TRANSPORT_INVOKED"]
    assert failed["billing"]["amount"] is None

    manager3 = RuntimeArtifactManager("paper3", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs3", archive_root=tmp_path / "archive3"))

    def timed_out(*_args, **_kwargs):
        raise TimeoutError("socket read deadline")

    monkeypatch.setattr("backend.env.model_client.urllib.request.urlopen", timed_out)
    manager3.activate()
    try:
        with pytest.raises(ModelTransportTimeout, match="socket read deadline"):
            client.complete([ChatMessage(role="user", content="input")])
    finally:
        manager3.deactivate()
    timeout_call = json.loads(next((manager3.run_dir / "llm_calls").glob("*.json")).read_text())
    assert timeout_call["status"] == "FAILED"
    assert timeout_call["error"]["type"] == "ModelTransportTimeout"


def test_completion_before_async_cancel_is_not_lost(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "outputs", archive_root=tmp_path / "archive"))
    common = {"alias": "test", "provider": "openai_compatible", "model": "test-model",
              "started_at": datetime.now(timezone.utc), "duration_ms": 0,
              "message_count": 1, "call_id": "same-call"}
    manager.record_model_call(ModelCallEvent(**common, phase="START"))
    manager.record_model_call(ModelCallEvent(**common, response=ModelResponse(
        content="answer", raw={"id": "remote-id"}, usage={"total_tokens": 4})))
    manager.record_model_call(ModelCallEvent(**common, phase="CANCELLED",
                                             error=asyncio.CancelledError()))
    call = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
    assert call["status"] == "CANCELLED"
    assert call["transport_completion_before_cancel"]["response"]["content"] == "answer"
    assert call["transport_completion_before_cancel"]["request_id"] == "remote-id"
