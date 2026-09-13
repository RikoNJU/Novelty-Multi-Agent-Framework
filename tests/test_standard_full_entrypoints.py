"""标准完整入口的 Reviewer fail-fast 契约。"""

from __future__ import annotations

import json
import sys

import pytest

from novelty_agent_framework.config import ReviewerRequiredError, load_application_config
from scripts import run_full_pipeline_experiment as experiment
from scripts import run_full_workflow_live as live


def _disabled_config():
    config = load_application_config()
    return config.model_copy(
        update={"reviewer": config.reviewer.model_copy(update={"enabled": False})}
    )


def test_paper_input_pipeline_fails_before_main_workflow(tmp_path, monkeypatch):
    paper_json = tmp_path / "paper.json"
    paper_json.write_text(
        json.dumps({"paper_id": "paper-1", "title": "Paper", "full_text": "body"}),
        encoding="utf-8",
    )
    output = tmp_path / "result.json"
    monkeypatch.setattr(live, "_load_dev_env", lambda: None)
    monkeypatch.setattr(live, "load_application_config", _disabled_config)
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

    with pytest.raises(
        ReviewerRequiredError, match=r"reviewer_required.*reviewer\.enabled=false"
    ):
        live.main()

    assert not output.exists()


def test_full_pipeline_fails_before_paper_processing(tmp_path, monkeypatch):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    experiment_dir = tmp_path / "experiment"
    monkeypatch.setattr(experiment, "EXPERIMENT_DIR", experiment_dir)
    monkeypatch.setattr(experiment, "_load_dev_env", lambda: None)
    monkeypatch.setattr(experiment, "load_application_config", _disabled_config)
    monkeypatch.setattr(
        experiment,
        "_configure_processor",
        lambda *_args: (_ for _ in ()).throw(AssertionError("paper processing started")),
    )
    monkeypatch.setattr(
        experiment.subprocess,
        "check_output",
        lambda command, **_kwargs: "lya\n" if "--show-current" in command else "deadbeef\n",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_full_pipeline_experiment.py",
            "--pdf",
            str(pdf),
            "--paper-id",
            "paper-1",
        ],
    )

    assert experiment.main() == 1

    metrics = json.loads((experiment_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["status"] == "INVALID / DEGRADED"
    assert "reviewer_required" in metrics["error"]
    assert "reviewer.enabled=false" in metrics["error"]
