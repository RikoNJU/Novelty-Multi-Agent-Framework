from __future__ import annotations

import json
import asyncio
import threading
from datetime import datetime, timezone
from pathlib import Path

from backend.env import (ChatMessage, ModelCallBudgetExceeded, ModelProfile, ModelResponse, ModelTraceError,
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
        await asyncio.to_thread(started.wait, 2)
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
