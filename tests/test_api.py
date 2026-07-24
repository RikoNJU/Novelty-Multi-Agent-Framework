"""论文查新可选 API 的任务生命周期测试。"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from novelty_agent_framework.main import create_app

ROOT = Path(__file__).resolve().parents[1]


def load_example(name: str) -> dict:
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


def test_novelty_health_and_run_lifecycle() -> None:
    with TestClient(create_app()) as client:
        health = client.get("/api/novelty/health")
        assert health.status_code == 200
        assert health.json()["workflow"] == "novelty"

        created = client.post(
            "/api/novelty/runs",
            json=load_example("paper.json"),
        )
        assert created.status_code == 202
        task_id = created.json()["task_id"]

        result = client.get(f"/api/novelty/runs/{task_id}")
        assert result.status_code == 200
        assert result.json()["status"] == "succeeded"
        assert result.json()["result"]["report"]["paper_id"] == "demo-paper-001"
def test_api_validates_input_and_returns_not_found() -> None:
    with TestClient(create_app()) as novelty_client:
        invalid = novelty_client.post(
            "/api/novelty/runs", json={"title": "缺少字段"}
        )
        assert invalid.status_code == 422
        assert novelty_client.get("/api/novelty/runs/not-found").status_code == 404
