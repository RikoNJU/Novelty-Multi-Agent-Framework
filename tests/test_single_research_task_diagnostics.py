from __future__ import annotations

import argparse
import asyncio
import json
from types import SimpleNamespace

import pytest

from conftest import minimal_search_plan
from novelty_agent_framework.core.runtime_artifacts import RuntimeDebugConfig
from novelty_agent_framework.schemas import (
    NoveltyPoint,
    ResearchTask,
    TaskResearchResult,
    TaskResearchStatus,
)
from scripts import run_single_research_task as single
from scripts.run_single_research_task import build_request, new_run_id, terminal_result


def _write_inputs(tmp_path):
    paper = tmp_path / "outputs" / "paper-1"
    paper.mkdir(parents=True)
    points = [
        NoveltyPoint(point_id="NP-1", claim="claim one", technical_features=["a"]),
        NoveltyPoint(point_id="NP-2", claim="claim two", technical_features=["b"]),
    ]
    tasks = [
        ResearchTask(task_id="T-1", novelty_point_id="NP-1", task_type="search", language="en"),
        ResearchTask(task_id="T-2", novelty_point_id="NP-2", task_type="search", language="zh"),
    ]
    (paper / "novelty-points.json").write_text(
        json.dumps({"novelty_points": [item.model_dump(mode="json") for item in points]}),
        encoding="utf-8",
    )
    (paper / "retrieval-plans.json").write_text(
        json.dumps(
            {
                "novelty_point_plans": [
                    {
                        "novelty_point_id": task.novelty_point_id,
                        "research_tasks": [task.model_dump(mode="json")],
                        "search_plans": [
                            minimal_search_plan(task.task_id, task.novelty_point_id).model_dump(
                                mode="json"
                            )
                        ],
                    }
                    for task in tasks
                ]
            }
        ),
        encoding="utf-8",
    )
    paper_json = tmp_path / "paper.json"
    paper_json.write_text(
        json.dumps({"paper_id": "paper-1", "title": "Paper", "full_text": "body"}),
        encoding="utf-8",
    )
    return tmp_path / "outputs", paper_json


def test_request_and_runtime_use_the_same_unique_run_id(tmp_path) -> None:
    output_root, _ = _write_inputs(tmp_path)
    run_id = new_run_id("T-2")

    request = build_request(
        output_root,
        "paper-1",
        run_id=run_id,
        point_id="NP-2",
        task_id="T-2",
    )

    assert request.run_id == run_id
    assert request.novelty_point.point_id == "NP-2"
    assert request.research_task.task_id == "T-2"


def test_exact_task_selectors_fail_clearly(tmp_path) -> None:
    output_root, _ = _write_inputs(tmp_path)

    with pytest.raises(SystemExit, match="必须按 ID 各精确匹配一次"):
        build_request(
            output_root,
            "paper-1",
            run_id="run-1",
            point_id="NP-2",
            task_id="missing",
        )


@pytest.mark.parametrize(
    ("task_status", "rejected", "expected"),
    [
        (TaskResearchStatus.COMPLETED, 0, ("SUCCESS", 0)),
        (TaskResearchStatus.COMPLETED, 1, ("SUCCESS", 2)),
        (TaskResearchStatus.PARTIAL, 0, ("SUCCESS", 2)),
        (TaskResearchStatus.FAILED, 0, ("SUCCESS", 1)),
    ],
)
def test_terminal_status_and_exit_code(task_status, rejected, expected) -> None:
    assert terminal_result(task_status, rejected) == expected


def test_main_persists_task_gate_outcome_and_finishes_once(tmp_path, monkeypatch) -> None:
    _, paper_json = _write_inputs(tmp_path)
    captured_requests = []

    class Researcher:
        tools = SimpleNamespace(names=("reader",))

        async def ainvoke(self, request):
            captured_requests.append(request)
            return TaskResearchResult(
                task_id=request.research_task.task_id,
                novelty_point_id=request.novelty_point.point_id,
                status=TaskResearchStatus.COMPLETED,
                steps_used=1,
            )

    class Gate:
        accepted = ()
        rejected = ()

        def audit(self):
            return {
                "validation_passed": True,
                "checked_card_count": 0,
                "accepted_card_count": 0,
                "rejected_card_count": 0,
                "accepted_card_ids": [],
                "rejected_card_ids": [],
                "rejected_cards": [],
            }

    real_manager = single.RuntimeArtifactManager
    managers = []

    class CountingManager(real_manager):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.finish_calls = 0
            managers.append(self)

        def finish_run(self, *args, **kwargs):
            self.finish_calls += 1
            return super().finish_run(*args, **kwargs)

    monkeypatch.setattr(single, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(single, "new_run_id", lambda _language: "single-fixed-run")
    monkeypatch.setattr(single, "load_application_config", lambda: {})
    monkeypatch.setattr(
        single,
        "build_workflow",
        lambda _config: SimpleNamespace(
            services=SimpleNamespace(task_researcher=Researcher())
        ),
    )
    monkeypatch.setattr(single, "validate_synthesis_input", lambda *args, **kwargs: Gate())
    monkeypatch.setattr(single, "RuntimeArtifactManager", CountingManager)
    monkeypatch.setattr(
        single,
        "RuntimeDebugConfig",
        lambda **kwargs: RuntimeDebugConfig(
            **kwargs, archive_root=tmp_path / "archive"
        ),
    )
    args = argparse.Namespace(paper_json=paper_json, point_id="NP-1", task_id="T-1")

    exit_code = asyncio.run(single.main(args))

    manager = managers[0]
    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert manager.finish_calls == 1
    assert captured_requests[0].run_id == manager.run_id == "single-fixed-run"
    assert [item["stage_name"] for item in summary["stages"]] == [
        "run_research_task",
        "validate_synthesis_input",
    ]
    assert summary["integrity_gates"][0]["validation_passed"] is True
    assert summary["outcome"]["task_status"] == "completed"
    assert summary["outcome"]["gate_a_validation_passed"] is True
    assert summary["run"]["entrypoint"] == "single_task"
    assert summary["run"]["input_identity"]["novelty_point_id"] == "NP-1"
    assert summary["run"]["input_identity"]["task_id"] == "T-1"


def test_researcher_exception_finishes_failed_and_does_not_run_gate(
    tmp_path, monkeypatch
) -> None:
    _, paper_json = _write_inputs(tmp_path)
    gate_called = False

    class FailingResearcher:
        tools = SimpleNamespace(names=("reader",))

        async def ainvoke(self, _request):
            raise RuntimeError("research failed")

    def unexpected_gate(*_args, **_kwargs):
        nonlocal gate_called
        gate_called = True
        raise AssertionError("Gate A must not run after a Researcher exception")

    monkeypatch.setattr(single, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(single, "new_run_id", lambda _task_id: "single-failed-run")
    monkeypatch.setattr(single, "load_application_config", lambda: {})
    monkeypatch.setattr(
        single,
        "build_workflow",
        lambda _config: SimpleNamespace(
            services=SimpleNamespace(task_researcher=FailingResearcher())
        ),
    )
    monkeypatch.setattr(single, "validate_synthesis_input", unexpected_gate)
    monkeypatch.setattr(
        single,
        "RuntimeDebugConfig",
        lambda **kwargs: RuntimeDebugConfig(
            **kwargs, archive_root=tmp_path / "archive"
        ),
    )

    exit_code = asyncio.run(
        single.main(
            argparse.Namespace(
                paper_json=paper_json, point_id="NP-1", task_id="T-1"
            )
        )
    )

    run_dir = tmp_path / "outputs/paper-1/runtime/single-failed-run"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert exit_code == 1
    assert gate_called is False
    assert manifest["status"] == "FAILED"
    assert summary["run"]["status"] == "FAILED"
    assert [item["status"] for item in summary["stages"]] == ["FAILED", "NOT_RUN"]
