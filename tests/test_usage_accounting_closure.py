"""Account actual provider consumption independently of request execution status."""
from __future__ import annotations

import asyncio
import json
import threading
from datetime import datetime, timezone

import pytest

from backend.env import (ChatMessage, ModelCallEvent, ModelClientError, ModelProfile,
    ModelResponse, OpenAICompatibleChatClient)
from novelty_agent_framework.core import RuntimeArtifactManager, RuntimeDebugConfig

USAGE = {"prompt_tokens": 1000, "completion_tokens": 500, "total_tokens": 1500,
    "prompt_tokens_details": {"cached_tokens": 200},
    "completion_tokens_details": {"reasoning_tokens": 100}}
MODEL = "deepseek-ai/DeepSeek-V4-Flash"


def manager_at(tmp_path):
    return RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "output", archive_root=tmp_path / "archive"))


def records(manager):
    return [json.loads(path.read_text()) for path in sorted((manager.run_dir / "llm_calls").glob("*.json"))]


def summary(manager):
    return json.loads((manager.run_dir / "summary.json").read_text())


def assert_consumption(totals, *, calls=1):
    assert totals["calls"] == calls
    assert totals["successful_calls"] == 0
    assert totals["failed_calls"] == calls
    assert totals["input_tokens"] == 1000 * calls
    assert totals["output_tokens"] == 500 * calls
    assert totals["cached_input_tokens"] == 200 * calls
    assert totals["reasoning_tokens"] == 100 * calls
    assert totals["total_tokens"] == 1500 * calls
    assert totals["priced_calls"] == calls
    assert totals["usage_unavailable_calls"] == 0
    assert totals["amount_rmb"] > 0
    assert totals["cost_completeness"] == "COMPLETE"


@pytest.mark.parametrize("order", ["cancel_then_complete", "complete_then_cancel"])
def test_cancellation_race_accounts_once_and_reconciles_finished_summary(tmp_path, order):
    manager = manager_at(tmp_path)
    common = {"alias": "priced", "provider": "openai_compatible", "model": MODEL,
        "started_at": datetime(2026, 9, 6, 19, tzinfo=timezone.utc), "duration_ms": 1,
        "message_count": 1, "call_id": "same-call"}
    complete = ModelCallEvent(**common, response=ModelResponse(content="ok", usage=USAGE, raw={"id": "response"}))
    cancelled = ModelCallEvent(**common, phase="CANCELLED", error=asyncio.CancelledError())
    manager.record_model_call(ModelCallEvent(**common, phase="START"))
    manager.record_model_call(ModelCallEvent(**common, phase="TRANSPORT_INVOKED"))
    first, second = (cancelled, complete) if order == "cancel_then_complete" else (complete, cancelled)
    manager.record_model_call(first)
    _, archive = manager.finish_run("FAILED")
    original_run = summary(manager)["run"]
    manager.record_model_call(second)
    # Duplicate event delivery is not an additional provider generation.
    manager.record_model_call(second)
    record = records(manager)[0]
    assert record["status"] == "CANCELLED"
    assert record["provider_usage"] == USAGE
    assert record["tokens"]["total_tokens"] == 1500
    assert record["billing"]["amount"] == 0.00348
    current = summary(manager)
    assert current["run"] == original_run
    assert_consumption(current["llm_usage"]["totals"])
    assert current["llm_usage"]["totals"]["amount_rmb"] == 0.00348
    assert json.loads((archive / "summary.json").read_text()) == current
    assert (archive / "summary.md").read_text() == (manager.run_dir / "summary.md").read_text()
    assert json.loads(next((archive / "llm_calls").glob("*.json")).read_text()) == record


class Response:
    status = 200
    headers = {}
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return None
    def read(self):
        return json.dumps(self.payload).encode()


def client():
    return OpenAICompatibleChatClient(ModelProfile(alias="priced", model=MODEL,
        base_url="http://fixture.invalid/v1", api_key="fixture"))


@pytest.mark.parametrize("choices", [[], [{"message": {"content": 17}}],
    [{"message": {"content": None, "tool_calls": [{"id": "call", "type": "function",
        "function": {"name": "reader", "arguments": "{bad-json"}}]}}]])
def test_response_parse_failure_keeps_provider_usage(monkeypatch, tmp_path, choices):
    raw = {"id": "malformed-response", "choices": choices, "usage": USAGE}
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response(raw))
    manager = manager_at(tmp_path)
    manager.activate()
    try:
        with pytest.raises(ModelClientError):
            client().complete([ChatMessage("user", "input")])
    finally:
        manager.finish_run("FAILED")
        manager.deactivate()
    record = records(manager)[0]
    assert record["status"] == "FAILED"
    assert record["provider_usage"] == USAGE
    assert record["request_id"] == "malformed-response"
    assert record["error"]["type"] == "ModelClientError"
    assert_consumption(summary(manager)["llm_usage"]["totals"])


@pytest.mark.parametrize("malformed", [False, True])
def test_cancelled_transport_completion_reconciles_late_usage(monkeypatch, tmp_path, malformed):
    entered, release = threading.Event(), threading.Event()
    class SlowMalformed(Response):
        def read(self):
            entered.set()
            assert release.wait(timeout=3)
            return super().read()
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: SlowMalformed(
        {"id": "late-response", "choices": [] if malformed else [{"message": {"content": "ok"}}], "usage": USAGE}))
    manager = manager_at(tmp_path)
    manager.activate()
    async def run():
        task = asyncio.create_task(client().acomplete([ChatMessage("user", "input")]))
        for _ in range(100):
            if entered.is_set():
                break
            await asyncio.sleep(0.01)
        assert entered.is_set()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        manager.finish_run("FAILED")
        original_run = summary(manager)["run"]
        release.set()
        for _ in range(100):
            if records(manager)[0].get("late_completion"):
                break
            await asyncio.sleep(0.01)
        assert records(manager)[0].get("late_completion")
        # Allow the writer to finish the atomic summary replacement as well.
        for _ in range(100):
            if summary(manager)["llm_usage"]["totals"]["total_tokens"] == 1500:
                break
            await asyncio.sleep(0.01)
        assert records(manager)[0]["status"] == "CANCELLED"
        assert records(manager)[0]["late_completion"]["status"] == ("FAILED" if malformed else "SUCCESS")
        assert records(manager)[0]["provider_usage"] == USAGE
        assert summary(manager)["run"] == original_run
        assert_consumption(summary(manager)["llm_usage"]["totals"])
    try:
        asyncio.run(run())
    finally:
        release.set()
        manager.deactivate()


def test_missing_usage_after_response_failure_remains_unknown(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response({"choices": []}))
    manager = manager_at(tmp_path)
    manager.activate()
    try:
        with pytest.raises(ModelClientError):
            client().complete([ChatMessage("user", "input")])
    finally:
        manager.finish_run("FAILED")
        manager.deactivate()
    assert records(manager)[0]["provider_usage"] == {}
    totals = summary(manager)["llm_usage"]["totals"]
    assert totals["usage_unavailable_calls"] == 1
    assert totals["amount_rmb"] is None
    assert totals["cost_completeness"] == "PARTIAL"


def test_transport_completes_before_coroutine_cancel_keeps_consumption(monkeypatch, tmp_path):
    from backend.env import reset_model_call_observer, set_model_call_observer

    persisted, release = threading.Event(), threading.Event()
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response(
        {"id": "completed-response", "choices": [{"message": {"content": "ok"}}], "usage": USAGE}))
    manager = manager_at(tmp_path)
    manager.activate()
    def observer(event):
        manager.record_model_call(event)
        if event.phase == "COMPLETE" and event.response is not None:
            persisted.set()
            assert release.wait(timeout=3)
    observer_token = set_model_call_observer(observer)
    async def run():
        task = asyncio.create_task(client().acomplete([ChatMessage("user", "input")]))
        for _ in range(100):
            if persisted.is_set():
                break
            await asyncio.sleep(0.01)
        assert persisted.is_set()
        assert records(manager)[0]["status"] == "SUCCESS"
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        manager.finish_run("FAILED")
        record = records(manager)[0]
        assert record["status"] == "CANCELLED"
        assert record["transport_completion_before_cancel"]["usage"] == USAGE
        assert record["provider_usage"] == USAGE
        assert_consumption(summary(manager)["llm_usage"]["totals"])
    try:
        asyncio.run(run())
    finally:
        release.set()
        reset_model_call_observer(observer_token)
        manager.deactivate()


def test_failed_response_then_repair_counts_two_distinct_attempts(monkeypatch, tmp_path):
    replies = iter([
        {"id": "failed", "choices": [], "usage": USAGE},
        {"id": "repair", "choices": [{"message": {"content": "repaired"}}],
         "usage": {"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10}},
    ])
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response(next(replies)))
    manager = manager_at(tmp_path)
    manager.activate()
    try:
        model = client()
        with pytest.raises(ModelClientError):
            model.complete([ChatMessage("user", "first")])
        assert model.complete([ChatMessage("user", "repair")]).content == "repaired"
    finally:
        manager.finish_run("SUCCESS")
        manager.deactivate()
    calls = records(manager)
    assert [call["status"] for call in calls] == ["FAILED", "SUCCESS"]
    assert len({call["client_call_id"] for call in calls}) == 2
    totals = summary(manager)["llm_usage"]["totals"]
    assert totals["calls"] == 2
    assert totals["successful_calls"] == totals["failed_calls"] == 1
    assert totals["input_tokens"] == 1007
    assert totals["output_tokens"] == 503
    assert totals["total_tokens"] == 1510
    assert totals["cost_completeness"] == "COMPLETE"


def test_cancelled_call_without_provider_usage_stays_unknown(tmp_path):
    manager = manager_at(tmp_path)
    common = {"alias": "priced", "provider": "openai_compatible", "model": MODEL,
        "started_at": datetime.now(timezone.utc), "duration_ms": 0,
        "message_count": 1, "call_id": "unreported"}
    manager.record_model_call(ModelCallEvent(**common, phase="START"))
    manager.record_model_call(ModelCallEvent(**common, phase="CANCELLED", error=asyncio.CancelledError()))
    manager.finish_run("FAILED")
    manager.record_model_call(ModelCallEvent(**common, response=ModelResponse(content="late without usage")))
    record = records(manager)[0]
    assert record["status"] == "CANCELLED"
    assert record["tokens"]["available"] is False
    totals = summary(manager)["llm_usage"]["totals"]
    assert totals["calls"] == 1
    assert totals["usage_unavailable_calls"] == 1
    assert totals["cost_completeness"] == "PARTIAL"
    assert totals["amount_rmb"] is None
