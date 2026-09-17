"""Web run budget reserves before transport and never recycles unknown requests."""

from decimal import Decimal
import json

import pytest

from backend.env import (ChatMessage, ModelCallBudgetExceeded, ModelCallOptions,
                         ModelProfile, OpenAICompatibleChatClient,
                         reset_model_call_budget, set_model_call_budget)
from novelty_agent_framework.services.model_budget import RunModelBudget


def test_shared_web_model_budget_stops_second_transport(tmp_path, monkeypatch):
    dispatches = []

    class Reply:
        status = 200
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps({"id": "reply", "choices": [{"message": {"content": "ok"}}],
                               "usage": {"prompt_tokens": 10, "completion_tokens": 2}}).encode()

    def urlopen(request, timeout):
        dispatches.append((request, timeout))
        return Reply()

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    profile = ModelProfile(alias="deepseek-flash", provider="openai_compatible",
                           model="deepseek-ai/DeepSeek-V4-Flash",
                           base_url="https://example.invalid/v1", api_key="test-only")
    client = OpenAICompatibleChatClient(profile)
    budget = RunModelBudget(tmp_path / "budget-ledger.json", cap_rmb=Decimal("1"), max_attempts=1)
    token = set_model_call_budget(budget)
    try:
        client.complete([ChatMessage(role="user", content="test")], options=ModelCallOptions(max_tokens=8))
        with pytest.raises(ModelCallBudgetExceeded):
            client.complete([ChatMessage(role="user", content="second")], options=ModelCallOptions(max_tokens=8))
    finally:
        reset_model_call_budget(token)
    assert len(dispatches) == 1
    ledger = json.loads((tmp_path / "budget-ledger.json").read_text())
    assert len(ledger["attempts"]) == 1
    assert ledger["attempts"][0]["status"] == "response_received"
    assert ledger["attempts"][0]["actual_bill_rmb"] is None
    assert ledger["reserved_total_rmb"] > 0


def test_failed_transport_keeps_unknown_charge_reserved(tmp_path, monkeypatch):
    calls = []

    def timeout(_request, *, timeout):
        calls.append(1)
        raise TimeoutError("test transport timeout")

    monkeypatch.setattr("urllib.request.urlopen", timeout)
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="deepseek-flash", provider="openai_compatible",
        model="deepseek-ai/DeepSeek-V4-Flash",
        base_url="https://example.invalid/v1", api_key="test-only"))
    budget = RunModelBudget(tmp_path / "budget-ledger.json", cap_rmb=Decimal("1"), max_attempts=1)
    token = set_model_call_budget(budget)
    try:
        with pytest.raises(Exception, match="模型传输超时"):
            client.complete([ChatMessage(role="user", content="test")], options=ModelCallOptions(max_tokens=8))
        with pytest.raises(ModelCallBudgetExceeded):
            client.complete([ChatMessage(role="user", content="retry")], options=ModelCallOptions(max_tokens=8))
    finally:
        reset_model_call_budget(token)
    ledger = json.loads((tmp_path / "budget-ledger.json").read_text())
    assert calls == [1]
    assert ledger["attempts"][0]["status"] == "failed_billing_unknown"
    assert ledger["attempts"][0]["actual_bill_rmb"] is None
    assert ledger["reserved_total_rmb"] > 0


def test_budget_resume_preserves_prior_unknown_attempt(tmp_path):
    path = tmp_path / "budget-ledger.json"
    path.write_text(json.dumps({
        "cap_rmb": 4.0, "max_attempts": 4, "reserved_total_rmb": 0.35817,
        "attempts": [{"attempt": 1, "reserved_rmb": 0.35817,
                      "status": "failed_billing_unknown", "actual_bill_rmb": None}],
    }))
    budget = RunModelBudget(path, cap_rmb=Decimal("4"), max_attempts=4, resume=True)
    assert budget._reserved == Decimal("0.35817")
    assert len(budget._attempts) == 1
    assert json.loads(path.read_text())["attempts"][0]["status"] == "failed_billing_unknown"
    with pytest.raises(ValueError, match="caps do not match"):
        RunModelBudget(path, cap_rmb=Decimal("5"), max_attempts=4, resume=True)
    with pytest.raises(FileExistsError):
        RunModelBudget(path, cap_rmb=Decimal("4"), max_attempts=4)
