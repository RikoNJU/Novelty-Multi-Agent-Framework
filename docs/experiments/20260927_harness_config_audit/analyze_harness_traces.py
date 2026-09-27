"""Read-only comparison of archived calls. No model/provider requests."""
from pathlib import Path
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
RUNS = [
    "docs/experiments/20260916_011551/run/MF2033k6lC/runtime/run-a8cd3083711c4fc19bc214f5e4e4ff12",
    "docs/experiments/runtime/MF2033k6lC_2026-09-17/run-d606cd37534a47349b905d42c6141768",
    *[str(p.relative_to(ROOT)) for p in sorted((ROOT / "docs/experiments/runtime/MF2033k6lC_2026-09-24").iterdir())],
]
KEYS = ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens", "total_tokens")

def read(path):
    return json.loads(path.read_text())

def analyze(relative):
    root = ROOT / relative
    summary = read(root / "summary.json")
    result = {"run": relative, "reader": {}, "calls": [], "usage_mismatches": []}
    counts, unique, repeated, empty, chars = Counter(), set(), [], [], 0
    for path in sorted((root / "tools").glob("*reader.json")):
        record = read(path)
        context = record.get("normalized_result") or {}
        if record.get("stage_name") not in {"run_research_task", None}:
            continue
        counts[record.get("execution_status", "unknown")] += 1
        rows = context.get("read_results", [context.get("read_result", {})])
        for row in rows:
            if not isinstance(row.get("char_start"), int):
                continue
            key = (json.dumps(record.get("scope", {}), sort_keys=True), row.get("namespace"),
                   row.get("artifact_id"), row["char_start"], row["char_end"])
            if key in unique:
                repeated.append(path.name)
            unique.add(key)
            chars += max(0, row["char_end"] - row["char_start"])
            if row["char_end"] == row["char_start"]:
                empty.append(path.name)
    result["reader"] = {"scope": "research task calls only (unscoped single-task included)",
        "execution_counts": dict(counts), "returned_chars": chars,
        "unique_intervals": len(unique), "repeated_intervals": repeated, "empty_reads": empty}
    summed = Counter()
    for path in sorted((root / "llm_calls").glob("*.json")):
        record = read(path)
        raw = record.get("provider_usage") or {}
        prompt = raw.get("prompt_tokens", raw.get("input_tokens", 0)) or 0
        output = raw.get("completion_tokens", raw.get("output_tokens", 0)) or 0
        details = raw.get("prompt_tokens_details") or raw.get("input_tokens_details") or {}
        completion = raw.get("completion_tokens_details") or raw.get("output_tokens_details") or {}
        calculated = {"input_tokens": prompt, "output_tokens": output,
            "total_tokens": raw.get("total_tokens", prompt + output),
            "cached_input_tokens": details.get("cached_tokens", 0),
            "reasoning_tokens": completion.get("reasoning_tokens", 0)}
        for key, value in calculated.items():
            if value != (record.get("tokens") or {}).get(key, 0):
                result["usage_mismatches"].append({"file": path.name, "key": key})
            summed[key] += value
        result["calls"].append({"file": path.name, "model": record.get("model"),
            "stage": record.get("stage_name"), "scope": record.get("scope"),
            "status": record.get("status"), "message_count": record.get("message_count"),
            "tokens": calculated, "billing_status": (record.get("billing") or {}).get("status"),
            "usage_available": bool(raw)})
    result["usage_sum"] = dict(summed)
    result["summary_totals"] = summary.get("llm_usage", {}).get("totals", {})
    for key in KEYS:
        if summed[key] != result["summary_totals"].get(key, 0):
            result["usage_mismatches"].append({"file": "summary.json", "key": key})
    result["research_results"] = []
    for path in sorted((root / "stages").glob("*run_research_task/output.json")):
        for task in read(path).get("task_research_results", []):
            result["research_results"].append({"stage": str(path.relative_to(root)),
                "task_id": task["task_id"], "point_id": task["novelty_point_id"],
                "status": task["status"], "reads": len(task.get("read_results", [])),
                "cards": len(task.get("evidence_cards", [])), "warnings": task.get("warnings", [])})
    return result

if __name__ == "__main__":
    output = Path(__file__).with_name("harness_trace_audit.json")
    results = [analyze(path) for path in RUNS]
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    for result in results:
        print(result["run"], json.dumps(result["reader"], ensure_ascii=False),
              "usage_mismatches", len(result["usage_mismatches"]),
              "cards", sum(row["cards"] for row in result["research_results"]))
