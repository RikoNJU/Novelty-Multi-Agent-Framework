"""Bounded local-only Researcher A/B over frozen archived artifacts.

This isolates Reader state from retrieval/network variance. It is not a full
workflow replay and does not compare scientific findings against the old run.
"""
from pathlib import Path
import asyncio
import hashlib
import json
import os
import sys
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src")]
from backend.env import ModelProfile, ModelCallOptions, OpenAICompatibleChatClient, PromptLibrary
from novelty_agent_framework.core import RuntimeArtifactManager, RuntimeDebugConfig
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import TaskResearchRequest
from novelty_agent_framework.tools import ReaderTool, ReferenceArtifactReaderTool, ResearcherToolRegistry, EvidenceCardBuilder
from novelty_agent_framework.workflows.research_task import TaskResearcherWorkflow, TaskResearcherConfig

# backend.env may load deployment proxy values from .env. Local loopback traffic
# must reach the local server directly; this does not change provider routing.
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost,::1"

BASE = ROOT / "docs/experiments/runtime/MF2033k6lC_2026-09-24/run-f41ac741cf6f49deaa52124ae5b23903"
OUT = Path(__file__).parent / "reader_local_pair_direct"

class FixtureWorkflow(TaskResearcherWorkflow):
    def _render_prompt(self, request):
        system, user = super()._render_prompt(request)
        fixture = json.loads((BASE / "tools/0002_database_search.json").read_text())["normalized_result"]
        return system, user + "\n\nThis is a frozen-candidate Reader experiment. Database search has already finished; no additional providers are enabled. Evaluate these existing candidates with Reader and produce the normal final draft.\n" + json.dumps(fixture, ensure_ascii=False)

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    input_path = BASE / "stages/0007_run_research_task/input.json"
    old = json.loads(input_path.read_text())
    request = TaskResearchRequest(subject_paper_id=old["subject_paper_id"], run_id="reader-local-pair",
        novelty_point=old["current_point"], research_task=old["current_task"],
        search_plan=old["current_search_plan"], target_identity=old["target_identity"])
    profile = ModelProfile(alias="local-qwen2.5-7b", model="qwen2.5-7b-instruct",
        base_url="http://127.0.0.1:8000/v1", api_key="local", context_window=32768,
        defaults={"timeout_seconds": 120, "max_tokens": 2048})
    snapshots = []
    for enabled in (False, True):
        label = "state_on" if enabled else "state_off"
        store = ReferenceStore(output_root=BASE / "workspace")
        config = TaskResearcherConfig(max_steps=10, max_tool_calls=8,
            max_chars_per_read=16000, max_total_read_chars=64000,
            per_tool_limits={"reader": 8}, reuse_reader_results=enabled,
            model_options=ModelCallOptions(temperature=0, max_tokens=2048, timeout_seconds=120, tool_choice="auto"))
        workflow = FixtureWorkflow(OpenAICompatibleChatClient(profile),
            ResearcherToolRegistry([ReaderTool(ReferenceArtifactReaderTool(store))]),
            EvidenceCardBuilder(store), prompts=PromptLibrary(ROOT / "backend/src/novelty_agent_framework/prompts"),
            config=config)
        runtime = RuntimeArtifactManager(request.subject_paper_id, run_id=label,
            config=RuntimeDebugConfig(output_root=OUT/label, archive_root=OUT/"archive",
                                      max_model_calls=14, max_physical_provider_requests=1))
        settings = {"endpoint": profile.base_url, "model": profile.model, "context_window": profile.context_window,
            "task_config": asdict(config), "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
            "source_runtime": str(BASE.relative_to(ROOT)), "only_ablation": "reuse_reader_results",
            "tool_names": ["reader"], "semantic_evidence_standard": "unchanged production EvidenceCardBuilder"}
        runtime.activate()
        try:
            stage = runtime.start_stage("run_research_task", request.model_dump(mode="json"))
            result, trace = await workflow._research(request)
            runtime.finish_stage(stage, result.model_dump(mode="json"))
            runtime.finish_run("SUCCESS" if result.status.value == "completed" else "FAILED")
        finally:
            runtime.deactivate()
        calls = [json.loads(p.read_text()) for p in sorted((runtime.run_dir/"llm_calls").glob("*.json"))]
        replayed = [e for e in trace if e.detail == "reader_state_reused"]
        snapshot = {"label": label, "settings": settings, "status": result.status,
            "llm_calls": len(calls), "input_tokens": sum(c["tokens"]["input_tokens"] for c in calls),
            "output_tokens": sum(c["tokens"]["output_tokens"] for c in calls),
            "reader_executions": sum(e.kind == "tool_call" for e in trace),
            "reader_replays": len(replayed), "reader_empty_results": sum(not r.text for r in result.read_results),
            "unique_read_ids": len({r.read_id for r in result.read_results}),
            "cards": len(result.evidence_cards), "warnings": result.warnings,
            "result": result.model_dump(mode="json")}
        snapshots.append(snapshot)
        (OUT / f"{label}.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+"\n")
        print(json.dumps({k:v for k,v in snapshot.items() if k not in {"settings","result"}}, ensure_ascii=False), flush=True)
    (OUT/"comparison.json").write_text(json.dumps(snapshots, ensure_ascii=False, indent=2)+"\n")

if __name__ == "__main__":
    asyncio.run(main())
