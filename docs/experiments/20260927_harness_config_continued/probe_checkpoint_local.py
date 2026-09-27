"""Guided, loopback-only Reader -> Qwen submit -> injected failure (max 2 calls).

Uses the existing authored Builder control fixture, not a real-paper accuracy set.
The named tool is forced at each turn to test the live plumbing, not autonomy.
"""
from __future__ import annotations
import asyncio
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src"), str(ROOT / "tests")]
from backend.env import ModelCallOptions, ModelProfile, OpenAICompatibleChatClient
from novelty_agent_framework.agents import DefaultEvidenceValidator
from novelty_agent_framework.core.integrity_gates import validate_synthesis_input
from novelty_agent_framework.tools import EvidenceCardBuilder, ReaderTool, ReferenceArtifactReaderTool, ResearcherToolRegistry
from novelty_agent_framework.workflows import TaskResearcherConfig, TaskResearcherWorkflow
from test_evidence_card_builder import prepare_store, scope, TEXT_A, TEXT_B

OUT = Path(__file__).parent / "checkpoint_local_guided"


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class GuidedClient:
    def __init__(self):
        self.raw = OpenAICompatibleChatClient(ModelProfile(alias="local-checkpoint-probe",
            model="qwen2.5-7b-instruct", base_url="http://127.0.0.1:8000/v1", api_key="local-placeholder",
            context_window=32768))
        self.calls = []
        self.ack = None

    async def acomplete(self, messages, *, options=None):
        for message in messages:
            if message.role != "tool" or not message.content:
                continue
            try:
                observation = json.loads(message.content)
            except (TypeError, ValueError):
                continue
            payload = observation.get("payload", observation)
            if payload.get("durable") and payload.get("accepted_card_ids"):
                self.ack = payload
                raise RuntimeError("injected_failure_after_acknowledged_evidence_checkpoint")
        if len(self.calls) >= 2:
            raise RuntimeError("guided_probe_two_call_cap_reached_without_checkpoint")
        name = "reader" if not self.calls else "submit_evidence"
        guidance = ("Controlled integration probe using an authored source fixture, not a scientific novelty claim. "
                    "First call reader with artifact_id=art_a, char_start=0, max_chars=1000. "
                    "After its successful response, submit one grounded card through submit_evidence. "
                    "Copy an exact quote from that Reader response. Do not finish before submitting.")
        messages = [replace(messages[0], content=messages[0].content + "\n" + guidance), *messages[1:]]
        options = replace(options, tool_choice={"type": "function", "function": {"name": name}})
        payload = self.raw._build_payload(messages, options)
        row = {"sequence": len(self.calls) + 1, "forced_tool": name, "request": payload,
               "request_sha256": sha(payload)}
        self.calls.append(row)
        started = time.monotonic()
        try:
            response = await self.raw.acomplete(messages, options=options)
            row.update(response=response.raw, response_sha256=sha(response.raw), usage=response.usage,
                       duration_seconds=time.monotonic()-started)
            return response
        except Exception as exc:
            row.update(error_type=type(exc).__name__, error=str(exc), duration_seconds=time.monotonic()-started)
            raise
        finally:
            (OUT / f"call-{row['sequence']}.json").write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n")


async def main():
    if OUT.exists():
        raise SystemExit("Refusing to overwrite prior live observations")
    OUT.mkdir()
    store = prepare_store(OUT / "outputs")
    manifest = store.load_manifest("paper-1")
    artifacts = []
    for artifact, content in zip(manifest.artifacts, (TEXT_A, TEXT_B), strict=True):
        store.write_document("paper-1", work_id=artifact.work_id, artifact_id=artifact.artifact_id,
                             extension="txt", content=content)
        artifacts.append(artifact.model_copy(update={"sha256": hashlib.sha256(content.encode()).hexdigest()}))
    store.persist_manifest("paper-1", manifest.model_copy(update={"artifacts": artifacts}))
    builder = EvidenceCardBuilder(store)
    client = GuidedClient()
    runner = TaskResearcherWorkflow(client,
        ResearcherToolRegistry([ReaderTool(ReferenceArtifactReaderTool(store))]), builder,
        config=TaskResearcherConfig(enable_evidence_checkpoint=True, max_steps=4, max_tool_calls=3,
            per_tool_limits={"reader": 1, "submit_evidence": 1},
            model_options=ModelCallOptions(max_tokens=1024, temperature=0.0, timeout_seconds=60)))
    request = scope().model_copy(update={"run_id": "checkpoint-guided-local-20260927"})
    result = await runner.ainvoke(request)
    (OUT / "result.json").write_text(result.model_dump_json(indent=2)+"\n")
    recovered = None
    if client.ack:
        recovered = runner.recover_checkpoint(request, invocation_id=client.ack["checkpoint_id"])
        (OUT / "recovered.json").write_text(recovered.model_dump_json(indent=2)+"\n")
    validation = DefaultEvidenceValidator().validate(result.evidence_cards, tasks=[request.research_task])
    gate = validate_synthesis_input(result.evidence_cards, evidence=result.evidence,
        tasks=[request.research_task], novelty_points=[request.novelty_point],
        paper_id=request.subject_paper_id, reference_store=store)
    summary = {"probe": "guided_local_tool_plumbing_not_autonomous_research", "model_calls": len(client.calls),
        "endpoint": "http://127.0.0.1:8000/v1", "source_fixture": "tests/test_evidence_card_builder.py",
        "fixture_kind": "authored_control_text", "fixture_sha256": sha([TEXT_A,TEXT_B]),
        "request_scope_sha256": sha(request.model_dump(mode="json")),
        "injected_failure_after_ack": bool(client.ack), "task_status": result.status.value,
        "builder_card_count": len(result.evidence_cards), "validator_accepted_count": len(validation.accepted),
        "integrity_gate_accepted_count": len(gate.accepted),
        "explicit_recovery_matches": bool(recovered and recovered.evidence == result.evidence
                                            and recovered.evidence_cards == result.evidence_cards),
        "usage": [row.get("usage") for row in client.calls], "warnings": result.warnings,
        "billing_status": "UNPRICED", "actual_local_inference_cost": None,
        "reviewer_executed": False, "retrieval_calls": 0}
    (OUT / "summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({key:summary[key] for key in ("model_calls","injected_failure_after_ack","task_status",
        "builder_card_count","validator_accepted_count","integrity_gate_accepted_count","explicit_recovery_matches")},ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
