"""Replay only the frozen report nodes; never launch upstream research."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import signal
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from backend.env import ModelResponse, reset_model_call_budget, set_model_call_budget
from novelty_agent_framework.agents import NoveltyCoordinatorAgent
from novelty_agent_framework.config import build_workflow
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager, RuntimeDebugConfig
from novelty_agent_framework.schemas import (
    EvidenceCard, InsufficientFinalEvidence, NoveltyBrief, NoveltyPoint,
    NoveltyPointReview, PaperInput, RejectedEvidence,
)
from novelty_agent_framework.services.model_budget import RunModelBudget


class OfflineDraftClient:
    """A declared test substitute; it never delegates to an external client."""

    def __init__(self, point_ids: list[str]):
        self.point_ids = point_ids
        self.calls = 0

    def complete(self, messages, *, options=None):
        self.calls += 1
        return ModelResponse(content=json.dumps({
            "conclusions": [{
                "novelty_point_id": point_id,
                "summary": "离线脚本模型测试文本；此处没有重新评价原 Reviewer 结论。",
                "supporting_card_ids": [], "counter_card_ids": [],
            } for point_id in self.point_ids],
            "limitations": ["此报告表达由离线测试替身生成，不是新的模型分析。"],
        }, ensure_ascii=False))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _typed_state(raw: dict) -> dict:
    state = dict(raw)
    state["paper"] = PaperInput.model_validate(raw["paper"])
    state["brief"] = NoveltyBrief.model_validate(raw["brief"])
    for key, model in (
        ("novelty_points", NoveltyPoint),
        ("evidence_cards", EvidenceCard),
        ("novelty_reviews", NoveltyPointReview),
        ("rejected_evidence", RejectedEvidence),
        ("insufficient_final_evidence_points", InsufficientFinalEvidence),
    ):
        state[key] = [model.model_validate(item) for item in raw.get(key, [])]
    return state


def _copy_renderer_inputs(source_input: Path, source_run_id: str, output_root: Path, paper_id: str) -> None:
    source_workspace = source_input.parents[5] / source_run_id
    target = output_root / paper_id
    for relative in (
        "paper-input/others/paper.json", "novelty-points.json", "retrieval-plans.json",
        "evidence-cards.json", "references/list.json", "candidate-audit.json",
    ):
        source = source_workspace / relative
        if source.is_file():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    required = ("paper-input/others/paper.json", "novelty-points.json",
                "retrieval-plans.json", "evidence-cards.json")
    missing = [name for name in required if not (target / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Renderer source artifacts missing: {missing}")


def _timeout_handler(signum, frame):
    raise TimeoutError("report_node_deadline_exceeded")


async def _one(row: dict, mode: str, deadline_seconds: int) -> dict:
    source = Path(row["synthesize_stage_input"])
    if _sha(source) != row["synthesize_stage_input_sha256"]:
        raise ValueError(f"source input hash mismatch: {row['label']}")
    raw = json.loads(source.read_text())
    prior_gate = raw.get("synthesis_integrity") or {}
    accepted_ids = {item["card_id"] for item in raw.get("evidence_cards", [])}
    if (prior_gate.get("validation_passed") is not True
            or set(prior_gate.get("accepted_card_ids", [])) != accepted_ids):
        raise ValueError("frozen upstream evidence gate does not match accepted cards")
    state = _typed_state(raw)
    if state["paper"].paper_id != row["paper_id"]:
        raise ValueError("source paper_id mismatch")
    output_root = Path(row["recovery_output_root"])
    if output_root.exists():
        raise FileExistsError(f"recovery output already exists: {output_root}")
    output_root.mkdir(parents=True)
    _copy_renderer_inputs(source, row["source_run_id"], output_root, row["paper_id"])
    workflow = build_workflow(output_root=output_root)
    if mode == "offline":
        fixture = OfflineDraftClient([point.point_id for point in state["novelty_points"]])
        configured = workflow.services.coordinator
        workflow.services = replace(workflow.services, coordinator=NoveltyCoordinatorAgent(
            model_client=fixture, prompts=configured._prompts,
            model_options=configured.model_options,
        ))
    else:
        fixture = None
    manager = RuntimeArtifactManager(
        row["paper_id"], run_id=row["recovery_id"],
        run_identity={"mode": "report_node_recovery", "source_run_id": row["source_run_id"],
                      "recovery_id": row["recovery_id"], "upstream_reused": True,
                      "upstream_recomputed": False},
        config=RuntimeDebugConfig(output_root=output_root,
                                  archive_root=output_root / "runtime-archive",
                                  max_model_calls=4),
        stage_names=("synthesize_report", "validate_report_integrity",
                     "persist_report", "render_report"),
    )
    result = {"mode": f"report_node_recovery_{mode}", "source_run_id": row["source_run_id"],
              "source_run_status": "FAILED", "recovery_id": row["recovery_id"],
              "paper_id": row["paper_id"], "upstream_reused": True,
              "upstream_recomputed": False, "recomputed_stages": [], "status": "RUNNING"}
    manager.activate()
    previous_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(deadline_seconds)
    try:
        for name, method in (
            ("synthesize_report", workflow._synthesize_report),
            ("validate_report_integrity", workflow._validate_report_integrity),
            ("persist_report", workflow._persist_report),
            ("render_report", workflow._render_report),
        ):
            update = await workflow._record_stage(name, method)(state)
            state.update(update)
            result["recomputed_stages"].append(name)
            if name == "validate_report_integrity" and not update["report_integrity"]["validation_passed"]:
                raise ValueError("report_integrity_failed: " + repr(update["report_integrity"]["issues"]))
        report_json = output_root / row["paper_id"] / "report.json"
        report_md = Path(state["rendered_report_path"])
        result.update(status="SUCCESS", report_json=str(report_json), report_json_sha256=_sha(report_json),
                      report_markdown=str(report_md), report_markdown_sha256=_sha(report_md),
                      point_ids=[item.novelty_point_id for item in state["report"].conclusions],
                      offline_fixture_calls=fixture.calls if fixture else None)
        manager.finish_run("SUCCESS")
    except BaseException as exc:
        result.update(status="FAILED", error_type=type(exc).__name__, error=str(exc)[:1000])
        manager.finish_run("FAILED", error=exc)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)
        manager.deactivate()
        (output_root / "recovery-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--mode", choices=("offline", "live"), required=True)
    parser.add_argument("--sources", nargs="+", default=["L1", "L2"])
    parser.add_argument("--budget-rmb", type=Decimal)
    parser.add_argument("--max-attempts", type=int)
    parser.add_argument("--deadline-seconds", type=int, default=240)
    parser.add_argument("--offline-tag", default="offline", help="append-only local output suffix")
    args = parser.parse_args()
    if args.mode == "live" and (args.budget_rmb is None or args.max_attempts is None):
        parser.error("live mode requires an explicitly approved total budget and attempt limit")
    manifest = json.loads(args.source_manifest.read_text())
    rows = {row["label"]: dict(row) for row in manifest["sources"]}
    for label in args.sources:
        if label not in rows:
            parser.error(f"unknown source {label}")
        if args.mode == "offline":
            rows[label]["recovery_output_root"] += "-" + args.offline_tag
    token = None
    if args.mode == "live":
        ledger_path = Path("outputs/report-node-recovery-20260918/model-budget-ledger.json")
        if ledger_path.exists():
            parser.error(f"live budget ledger already exists; refusing a reset: {ledger_path}")
        budget = RunModelBudget(ledger_path,
                                cap_rmb=args.budget_rmb, max_attempts=args.max_attempts)
        token = set_model_call_budget(budget)
    try:
        for label in args.sources:
            result = asyncio.run(_one(rows[label], args.mode, args.deadline_seconds))
            print(json.dumps(result, ensure_ascii=False))
            if result["status"] != "SUCCESS":
                break
    finally:
        if token is not None:
            reset_model_call_budget(token)


if __name__ == "__main__":
    main()
