from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from backend.env import ChatMessage, ModelProfile, OpenAICompatibleChatClient
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
