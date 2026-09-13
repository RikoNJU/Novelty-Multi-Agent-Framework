from __future__ import annotations

import json
import sys
from types import SimpleNamespace

from scripts import run_full_workflow_live as live


def test_paper_input_entrypoint_passes_stable_identity(tmp_path, monkeypatch) -> None:
    paper_json = tmp_path / "paper.json"
    paper_json.write_text(
        json.dumps({"paper_id": "paper-1", "title": "Paper", "full_text": "body"}),
        encoding="utf-8",
    )
    output = tmp_path / "result.json"
    captured = {}

    class Result:
        def model_dump_json(self):
            return json.dumps({"ok": True})

    class Workflow:
        def run(self, paper, *, run_identity=None):
            captured["paper"] = paper
            captured["run_identity"] = run_identity
            return Result()

    config = SimpleNamespace(
        project=SimpleNamespace(
            workflow=SimpleNamespace(max_rounds=None, max_concurrency=None)
        )
    )
    monkeypatch.setattr(live, "_load_dev_env", lambda: None)
    monkeypatch.setattr(live, "load_application_config", lambda: config)
    monkeypatch.setattr(live, "build_standard_full_workflow", lambda _config: Workflow())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_full_workflow_live.py",
            "--paper-json",
            str(paper_json),
            "--output",
            str(output),
        ],
    )

    live.main()

    identity = captured["run_identity"]
    assert captured["paper"].paper_id == "paper-1"
    assert identity["entrypoint"] == "paper_input"
    assert len(identity["input_identity"]["paper_sha256"]) == 64
    assert identity["input_identity"]["novelty_point_id"] is None
    assert json.loads(output.read_text(encoding="utf-8")) == {"ok": True}
