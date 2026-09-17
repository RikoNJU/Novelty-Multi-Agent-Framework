"""Run the fixed NP-3 Reviewer-only L0/L1 pair from the archived review input."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from backend.env import ModelCallOptions
from novelty_agent_framework.agents.evidence_reviewer import EvidenceReviewerConfig, NoveltyEvidenceReviewer
from novelty_agent_framework.config.factory import build_model_registry, build_prompt_library
from novelty_agent_framework.config.loader import load_application_config
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager, RuntimeDebugConfig
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import EvidenceCard, Evidence, NoveltyPoint, NoveltyPointReviewRequest, ResearchTask
from novelty_agent_framework.tools.reader import ReviewerReaderTool
from novelty_agent_framework.tools.reference_reader import ReferenceArtifactReaderTool
from novelty_agent_framework.tools.researcher_registry import ResearcherToolRegistry


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/experiments/20260917_214820_retrieval_repair/runs/full/0001/MF2033k6lC"
STAGE_INPUT = SOURCE / "runtime/run-d606cd37534a47349b905d42c6141768/stages/0012_review_evidence/input.json"
EXPERIMENT = ROOT / "docs/experiments/20260918_000421_reviewer_evidence_repair"
PAPER = "MF2033k6lC"
CARD_IDS = ("card_055dcd710a45194158c1d5ba", "card_927caf724042beff967b2231")
ABSTRACT_IDS = {"art_082358a7cb0efe62d471f7fb", "art_044b624240993e16c40f3537"}
MODEL_CALL_LIMIT = 20
MAX_REQUEST_BYTES = 60_000
MAX_OUTPUT_TOKENS = 2048
COST_CAP_RMB = 4.00
INPUT_RATE = 3.0 / 1_000_000
OUTPUT_RATE = 9.0 / 1_000_000


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class AbstractReader(ReviewerReaderTool):
    def material_catalog(self, scope):
        return [item for item in super().material_catalog(scope) if item["artifact_id"] in ABSTRACT_IDS]


class BudgetedClient:
    def __init__(self, inner, ledger):
        self.inner, self.ledger = inner, ledger

    async def acomplete(self, messages, *, options=None):
        options = options or ModelCallOptions()
        payload = self.inner._build_payload(messages, options)
        size = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        if size > MAX_REQUEST_BYTES:
            raise RuntimeError(f"model input exceeds frozen byte cap: {size}")
        tokens = options.max_tokens or MAX_OUTPUT_TOKENS
        if tokens > MAX_OUTPUT_TOKENS:
            raise RuntimeError("model output token cap exceeded")
        bound = size * INPUT_RATE + tokens * OUTPUT_RATE
        if len(self.ledger["calls"]) >= MODEL_CALL_LIMIT or self.ledger["reserved_rmb"] + bound > COST_CAP_RMB:
            raise RuntimeError("frozen Reviewer-only budget exhausted")
        call = {"request_bytes": size, "max_output_tokens": tokens, "worst_case_rmb": round(bound, 6), "started_at": datetime.now(timezone.utc).isoformat()}
        self.ledger["calls"].append(call)
        self.ledger["reserved_rmb"] += bound
        try:
            response = await self.inner.acomplete(messages, options=options)
            call["usage"] = dict(response.usage)
            call["completed_at"] = datetime.now(timezone.utc).isoformat()
            return response
        except Exception as exc:
            call["error"] = f"{type(exc).__name__}: {exc}"[:300]
            raise


def build_request(raw):
    point = NoveltyPoint.model_validate(next(p for p in raw["novelty_points"] if p["point_id"] == "NP-3"))
    cards = [EvidenceCard.model_validate(c) for c in raw["validator_accepted_cards"] if c["card_id"] in CARD_IDS]
    assert {c.card_id for c in cards} == set(CARD_IDS)
    cited = {e for card in cards for e in card.evidence_ids}
    evidence = [Evidence.model_validate(e) for e in raw["raw_evidence"] if e["evidence_id"] in cited]
    assert {e.evidence_id for e in evidence} == cited
    tasks = [ResearchTask.model_validate(t) for t in raw["all_research_tasks"] if t["novelty_point_id"] == "NP-3"]
    return NoveltyPointReviewRequest(subject_paper_id=PAPER, novelty_point=point, tasks=tasks, cards=cards, evidence=evidence)


async def run_variant(variant, request, registry, prompts, ledger, trial_root):
    output = trial_root / variant / "outputs"
    destination = output / PAPER / "references"
    shutil.copytree(SOURCE / "references", destination)
    reader_cls = AbstractReader if variant == "L0" else ReviewerReaderTool
    reader = reader_cls(ReferenceArtifactReaderTool(ReferenceStore(output_root=output)))
    model = BudgetedClient(registry.client_for("deepseek-flash"), ledger)
    reviewer = NoveltyEvidenceReviewer(
        model_client=model, prompts=prompts, tool_registry=ResearcherToolRegistry([reader]),
        config=EvidenceReviewerConfig(enabled=True, max_steps=5, max_tool_calls=4,
                                      max_total_read_chars=8000, card_timeout_seconds=240,
                                      summary_timeout_seconds=180),
        model_options=ModelCallOptions(temperature=0, max_tokens=MAX_OUTPUT_TOKENS,
                                       timeout_seconds=90, tool_choice="auto",
                                       extra_body={"enable_thinking": False}),
    )
    manager = RuntimeArtifactManager(PAPER, config=RuntimeDebugConfig(
        output_root=output, archive_root=trial_root / variant / "archive",
        max_model_calls=10, max_physical_provider_requests=1),
        run_id=f"rv-np3-{variant.lower()}", model_provider="siliconflow",
        model_name="deepseek-ai/DeepSeek-V4-Flash", enabled_tools=["reader"],
        stage_names=["review_card", "summarize_reviews"],
        runtime_config={"variant": variant, "max_steps": 5, "max_tool_calls": 4,
                        "max_total_read_chars_per_card": 8000, "max_output_tokens": MAX_OUTPUT_TOKENS,
                        "cost_cap_rmb_pair": COST_CAP_RMB})
    rows = []
    manager.activate()
    try:
        for index, card in enumerate(request.cards):
            single = NoveltyPointReviewRequest(
                subject_paper_id=PAPER, novelty_point=request.novelty_point,
                tasks=request.tasks, cards=[card],
                evidence=[e for e in request.evidence if e.evidence_id in card.evidence_ids])
            handle = manager.start_stage("review_card", {"point_id": "NP-3", "card_id": card.card_id,
                                                           "variant_id": variant, "request": single.model_dump(mode="json")})
            review = await reviewer.review_card(single)
            row = {"index": index, "card_id": card.card_id, "novelty_point_id": "NP-3",
                   "status": "completed", "review": review.model_dump(mode="json")}
            rows.append(row)
            manager.finish_stage(handle, row)
            save(trial_root / variant / f"card-{index + 1}.json", row)
        handle = manager.start_stage("summarize_reviews", {"point_id": "NP-3", "variant_id": variant,
                                                                  "card_reviews": rows})
        result = await reviewer.summarize_reviews(request, rows)
        manager.finish_stage(handle, result.model_dump(mode="json"))
        save(trial_root / variant / "summary-review.json", result.model_dump(mode="json"))
        manager.finish_run("SUCCESS")
        return result.model_dump(mode="json")
    except BaseException as exc:
        manager.finish_run("FAILED", error=exc)
        raise
    finally:
        manager.deactivate()


async def main(trial_root):
    raw = json.loads(STAGE_INPUT.read_text(encoding="utf-8"))
    request = build_request(raw)
    cfg = load_application_config()
    registry = build_model_registry(cfg)
    client = registry.client_for("deepseek-flash")
    if not client.profile.api_key:
        raise RuntimeError("SILICONFLOW_API_KEY unavailable")
    prompts = build_prompt_library()
    ledger = {"calls": [], "reserved_rmb": 0.0, "cap_rmb": COST_CAP_RMB}
    save(trial_root / "frozen-input.json", request.model_dump(mode="json"))
    save(trial_root / "preflight.json", {
        "source_stage_input": str(STAGE_INPUT.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(STAGE_INPUT.read_bytes()).hexdigest(),
        "variants": ["L0", "L1"], "model": "deepseek-ai/DeepSeek-V4-Flash",
        "model_call_limit_pair": MODEL_CALL_LIMIT, "max_request_bytes": MAX_REQUEST_BYTES,
        "max_output_tokens_per_call": MAX_OUTPUT_TOKENS, "max_tool_calls_per_card": 4,
        "max_read_chars_per_card": 8000, "card_timeout_seconds": 240,
        "summary_timeout_seconds": 180, "format_retries": "production bounded repair only",
        "cost_cap_rmb_pair": COST_CAP_RMB,
    })
    try:
        for variant in ("L0", "L1"):
            result = await run_variant(variant, request, registry, prompts, ledger, trial_root)
            save(trial_root / f"{variant}-result.json", result)
            save(trial_root / "budget-ledger.json", ledger)
    finally:
        save(trial_root / "budget-ledger.json", ledger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trial_root", type=Path)
    args = parser.parse_args()
    asyncio.run(main(args.trial_root.resolve()))
