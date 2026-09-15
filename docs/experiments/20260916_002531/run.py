"""Compare reviewers on frozen eight-card evidence; no retrieval or MinerU."""
import asyncio
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src"), str(ROOT / "scripts")]
from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import load_application_config, build_standard_full_workflow, effective_safe_config
from novelty_agent_framework.schemas import PaperInput, NoveltyPoint, ResearchTask, Evidence, EvidenceCard
from run_full_pipeline_experiment import Recorder

BASE = Path(__file__).resolve().parent
SOURCE = ROOT / "docs/experiments/20260915_224229/run/MF2033k6lC"
INPUT = SOURCE / "runtime/run-9e5fd9b6a2c841078c9602a551f2448c/stages/0029_review_evidence/input.json"

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))

async def main():
    _load_dev_env()
    recorder = Recorder()
    recorder.install_model_hook()
    source = json.loads(INPUT.read_text())
    state = {"paper": PaperInput.model_validate(source["paper"])}
    for key, cls in [("novelty_points", NoveltyPoint), ("all_research_tasks", ResearchTask),
                     ("raw_evidence", Evidence), ("validator_accepted_cards", EvidenceCard),
                     ("evidence_cards", EvidenceCard), ("raw_evidence_cards", EvidenceCard)]:
        state[key] = [cls.model_validate(row) for row in source.get(key, [])]
    write(BASE / "input.json", source)
    metrics = []
    for mode in ("point_parallel", "card_parallel_summary"):
        out = BASE / mode
        out.mkdir(exist_ok=False)
        for name in ("references", "subject_references"):
            shutil.copytree(SOURCE / name, out / "MF2033k6lC" / name)
        config = load_application_config()
        config.project.runtime_debug.archive_root = str(out / "archive")
        workflow = build_standard_full_workflow(config, output_root=out)
        reviewer = workflow.services.reviewer
        if mode == "point_parallel":
            class Baseline:
                async def review(self, request):
                    return await reviewer.review(request)
            workflow.services.reviewer = Baseline()
        write(out / "effective_config.json", effective_safe_config(config))
        started = time.monotonic()
        before = len(recorder.model_calls)
        print(mode, "start", datetime.now().isoformat(), flush=True)
        try:
            result = await workflow._review_evidence(state)
            write(out / "result.json", {
                key: [x.model_dump(mode="json") for x in value]
                for key, value in result.items()
            })
            row = {"mode": mode, "status": "complete", "elapsed_seconds": time.monotonic() - started,
                   "reviews": [x.model_dump(mode="json") for x in result["novelty_reviews"]]}
        except Exception as exc:
            row = {"mode": mode, "status": "failed", "error": type(exc).__name__}
        calls = recorder.model_calls[before:]
        row.update(model_calls=len(calls), tokens=sum(x.get("total_tokens") or 0 for x in calls))
        write(out / "model_calls.json", calls)
        metrics.append(row)
        write(BASE / "metrics.json", metrics)
        print(mode, row["status"], row.get("elapsed_seconds"), flush=True)
    print("FINISHED", datetime.now().astimezone().strftime("%Y%m%d_%H%M%S"), flush=True)

asyncio.run(main())
