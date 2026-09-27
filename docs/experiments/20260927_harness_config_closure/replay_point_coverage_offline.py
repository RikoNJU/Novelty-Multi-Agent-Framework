"""Replay frozen candidate/response observations through both guard policies.

All responses are fixed local fixtures. No LLM, retrieval or network calls.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src")]
from backend.env import ModelResponse
from novelty_agent_framework.agents.point_extractor import NoveltyPointExtractorAgent
from novelty_agent_framework.schemas import PaperDigest

FIXTURE = ROOT / "tests/fixtures/extractor/historical_dedup_20260924.json"
OUT = Path(__file__).resolve().parent / "point_coverage_holdout"


class FixedClient:
    def __init__(self, fixture):
        self.rows = iter([{"novelty_points": fixture["candidates"]}, fixture["mapped_response"], {"novelty_points": []}])
        self.calls = 0
    def complete(self, messages, *, options=None):
        self.calls += 1
        return ModelResponse(content=json.dumps(next(self.rows), ensure_ascii=False))


def main():
    OUT.mkdir(exist_ok=True)
    fixture = json.loads(FIXTURE.read_text())
    results = []
    for enabled in (False, True):
        client = FixedClient(copy.deepcopy(fixture))
        agent = NoveltyPointExtractorAgent(client, conservative_dedup=enabled)
        points = agent.extract(PaperDigest.model_validate(fixture["digest"]), previous_brief=None, attempt=1)
        ledger = agent.last_trace["coverage_ledger"]
        row = {"conservative_dedup": enabled, "stub_calls": client.calls,
            "actual_model_calls": 0, "final_point_count": len(points),
            "deleted_indices": agent.last_trace["deduplication"]["deleted_indices"],
            "pending_indices": agent.last_trace["deduplication"]["pending_indices"],
            "candidate_features_preserved": ledger["candidate_features_preserved"],
            "feature_count": len(ledger["features"]),
            "unpreserved_feature_count": sum(not feature["final_point_ids"] for feature in ledger["features"]),
            "coverage_complete": ledger["coverage_complete"],
            "semantic_coverage_verified": ledger["semantic_coverage_verified"]}
        name = "guarded" if enabled else "legacy_mapped"
        (OUT / f"{name}.json").write_text(json.dumps({"result": row, "trace": agent.last_trace}, ensure_ascii=False, indent=2) + "\n")
        results.append(row)
    (OUT / "summary.json").write_text(json.dumps({"fixture": str(FIXTURE.relative_to(ROOT)),
        "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "source_trace_sha256": fixture["source_trace_sha256"],
        "source_mapped_response_sha256": fixture["source_mapped_response_sha256"],
        "input_changed": False, "model_output_changed": False,
        "actual_model_calls": 0, "retrieval_calls": 0, "results": results}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
