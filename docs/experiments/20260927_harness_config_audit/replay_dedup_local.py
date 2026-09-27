"""Two bounded, loopback-only calls on frozen historical candidates; no retrieval."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend/src"))
from backend.env import PromptLibrary
from novelty_agent_framework.agents.point_extractor import DELETE_SCHEMA, _validated_deletion_mappings

OUT = Path(__file__).parent / "dedup_local_pair"
HISTORY = ROOT / "docs/experiments/runtime/MF2033k6lC_2026-09-24/run-f41ac741cf6f49deaa52124ae5b23903"


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    old = json.loads((HISTORY / "llm_calls/0002_local-qwen2.5-7b.json").read_text())
    trace = json.loads((HISTORY / "diagnostics/point_extraction_trace.json").read_text())
    old_payload = old["request_payload"]
    rendered = PromptLibrary(ROOT / "backend/src/novelty_agent_framework/prompts").render(
        "reviewer/review_points",
        points_json=json.dumps(trace["deduplication"]["input"], ensure_ascii=False),
        contribution_context_json=json.dumps(trace["deduplication"]["contribution_context"], ensure_ascii=False),
        delete_schema=json.dumps(DELETE_SCHEMA, ensure_ascii=False),
    )
    new_payload = copy.deepcopy(old_payload)
    new_payload["messages"] = [{"role": "system", "content": rendered.system},
                               {"role": "user", "content": rendered.user}]
    manifest = {
        "historical_run_id": old["run_id"], "endpoint": "http://127.0.0.1:8000/v1/chat/completions",
        "candidate_sha256": digest(trace["deduplication"]["input"]),
        "contribution_context_sha256": digest(trace["deduplication"]["contribution_context"]),
        "historical_digest_sha256": trace["digest_sha256"],
        "options_equal": {k: v for k, v in old_payload.items() if k != "messages"} ==
                         {k: v for k, v in new_payload.items() if k != "messages"},
        "calls_limit": 2, "concurrency": 1, "retrieval_calls": 0,
        "scope": "One completion per output contract; not a semantic accuracy benchmark.",
    }
    results = []
    for label, payload in (("legacy", old_payload), ("mapped", new_payload)):
        target = OUT / f"{label}.json"
        if target.exists():
            raise SystemExit(f"Refusing to overwrite an existing paid/compute observation: {target}")
        started = time.monotonic()
        row = {"variant": label, "request": payload, "request_sha256": digest(payload)}
        try:
            req = urllib.request.Request(manifest["endpoint"],
                data=json.dumps(payload, ensure_ascii=False).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=90) as response:
                body = json.load(response)
            row.update(response=body, response_sha256=digest(body), duration_seconds=time.monotonic() - started)
            content = body["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            row["parsed_output"] = parsed
            row["current_harness_audit"] = _validated_deletion_mappings(parsed, len(trace["deduplication"]["input"]))
        except Exception as exc:
            row.update(error_type=type(exc).__name__, error=str(exc), duration_seconds=time.monotonic() - started)
        target.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n")
        results.append({"variant": label, "error": row.get("error"),
                        "parsed_output": row.get("parsed_output"),
                        "usage": row.get("response", {}).get("usage"),
                        "duration_seconds": row["duration_seconds"]})
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    manifest["results"] = results
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
