"""只跑一个 ResearchTask，直接观察能否产出证据卡。

用于在完整流程之前定位 Researcher 层的问题：不跑 Coordinator、Validator、
Reviewer 与报告生成，只把绑定的 NoveltyPoint + ResearchTask 交给
TaskResearcherWorkflow，并顺带跑一遍 Gate A，把「读到了什么」与「留下了什么卡」
分开看。运行记录照常写入 outputs/<paper_id>/runtime/，可交给
scripts/reader_failure_diagnostics.py 分析。

用法::

    python scripts/run_single_research_task.py --paper-id MF2033k6lC --language en
    python scripts/run_single_research_task.py --paper-id MG19333vrw --language zh
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "src"))

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / "backend" / ".env")
except Exception:
    pass

from novelty_agent_framework.config.factory import build_workflow
from novelty_agent_framework.config.loader import load_application_config
from novelty_agent_framework.core.runtime_artifacts import (
    RuntimeArtifactManager,
    RuntimeDebugConfig,
)
from novelty_agent_framework.schemas import (
    NoveltyPoint,
    ResearchTask,
    SearchPlan,
    TaskResearchRequest,
)


def build_request(output_root: Path, paper_id: str, language: str) -> TaskResearchRequest:
    points = {
        item["point_id"]: NoveltyPoint.model_validate(item)
        for item in json.loads(
            (output_root / paper_id / "novelty-points.json").read_text(encoding="utf-8")
        )["novelty_points"]
    }
    plans = json.loads(
        (output_root / paper_id / "retrieval-plans.json").read_text(encoding="utf-8")
    )["novelty_point_plans"]

    for entry in plans:
        point_id = entry["novelty_point_id"]
        by_task = {item["task_id"]: item for item in entry["search_plans"]}
        for raw_task in entry["research_tasks"]:
            if raw_task.get("language") != language:
                continue
            task = ResearchTask.model_validate(raw_task)
            return TaskResearchRequest(
                subject_paper_id=paper_id,
                run_id=f"single-{language}",
                novelty_point=points[point_id],
                research_task=task,
                search_plan=SearchPlan.model_validate(by_task[task.task_id]),
            )
    raise SystemExit(f"没有 language={language!r} 的任务")


async def main(args: argparse.Namespace) -> int:
    output_root = PROJECT_ROOT / "outputs"
    request = build_request(output_root, args.paper_id, args.language)
    label = f"{request.novelty_point.point_id}/{request.research_task.task_id}"
    print(f"论文 : {args.paper_id}")
    print(f"任务 : {label}  language={request.research_task.language}")
    print(f"查新点: {request.novelty_point.claim[:90]}")

    workflow = build_workflow(load_application_config())
    researcher = workflow.services.task_researcher
    print(f"工具表: {researcher.tools.names}")

    manager = RuntimeArtifactManager(
        args.paper_id,
        config=RuntimeDebugConfig(enabled=True, output_root=output_root),
        run_id=f"single-{args.language}-{int(time.time())}",
        runtime_config={"probe": "single-english-task", "task": label},
        enabled_tools=list(researcher.tools.names),
        stage_names=["run_research_task"],
    )
    manager.activate()
    started = time.perf_counter()
    try:
        result = await researcher.ainvoke(request)
    finally:
        manager.finish_run("SUCCESS")
        manager.deactivate()

    print(f"\n耗时 {time.perf_counter() - started:.1f}s  run 目录: {manager.run_dir}")
    print(f"状态      : {result.status}")
    print(f"读取次数  : {len(result.read_results or [])}")
    print(f"证据卡    : {len(result.evidence_cards or [])}")
    print(f"证据条数  : {len(result.evidence or [])}")
    print(f"步数      : {result.steps_used}")
    for warning in result.warnings or []:
        print(f"  warning : {warning[:180]}")
    for card in result.evidence_cards or []:
        print(f"\n  卡片 {card.card_id}")
        print(f"    文献   : {card.document_title}")
        print(f"    证据数 : {len(card.evidence_ids)}")
        print(f"    主贡献 : {str(card.main_contribution)[:120]}")

    # 让产出的卡过一遍 Gate A（含命名空间感知与逐字/定位校验）
    from novelty_agent_framework.core.integrity_gates import validate_synthesis_input
    from novelty_agent_framework.persistence import ReferenceStore

    gate = validate_synthesis_input(
        result.evidence_cards or [],
        evidence=result.evidence or [],
        tasks=[request.research_task],
        novelty_points=[request.novelty_point],
        paper_id=args.paper_id,
        reference_store=ReferenceStore(output_root),
    )
    print(
        f"\nGate A   : 通过 {len(gate.accepted)} / 拒绝 {len(gate.rejected)}"
        f"  validation_passed={gate.audit()['validation_passed']}"
    )
    for card, reasons in gate.rejected:
        print(f"  拒绝 {card.card_id}: {'; '.join(reasons)[:200]}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-id", default="MF2033k6lC")
    parser.add_argument("--language", default="en")
    raise SystemExit(asyncio.run(main(parser.parse_args())))
