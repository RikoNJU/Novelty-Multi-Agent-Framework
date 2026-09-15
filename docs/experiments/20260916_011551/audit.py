"""Check this cached full-run experiment's persisted outputs, without network."""
import hashlib
import json
import re
from pathlib import Path

base = Path(__file__).resolve().parent
run = base / "run"
paper = run / "MF2033k6lC"
def read(p):
    return json.loads(p.read_text())

result = read(run / "result.json")
report = (paper / "report/MF2033k6lC-report.md").read_text()
cache = read(paper / "subject_references/list.json")
for artifact in cache["artifacts"]:
    path = paper / "subject_references" / artifact["relative_path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]
assert len(cache["artifacts"]) == 9
assert read(run / "run.json")["status"] == "SUCCESS"
assert len(result["evidence_cards"]) == 4
tasks = [read(p) for p in paper.glob("research-runs/*/*/attempt-*.json")]
evidence = {e["evidence_id"]: e for task in tasks for e in task["evidence"]}
card_ids = {c["card_id"] for c in result["evidence_cards"]}
for card in result["evidence_cards"]:
    for eid in card["evidence_ids"]:
        e = evidence[eid]
        assert e["novelty_point_id"] == card["novelty_point_id"]
        assert e["provenance"]["artifact_namespace"] == "subject_reference"
for review in result["novelty_reviews"]:
    for work in review["highly_relevant_works"]:
        assert set(work["card_ids"]) <= card_ids
        assert set(work["evidence_ids"]) <= evidence.keys()
checkpoint = read(paper / "novelty-reviews.json")
assert checkpoint["phase"] == "complete"
assert [row["index"] for row in checkpoint["card_reviews"]] == [1, 2, 3, 4]
assert all(row["status"] == "completed" for row in checkpoint["card_reviews"])
section = report.split("### 5.3 检索式")[1].split("\n---")[0]
query_counts = {point: len(re.findall(r"  - `", body)) for point, body in
                re.findall(r"- \*\*(NP-\d+)\*\*(.*?)(?=\n- \*\*NP-|\Z)", section, re.S)}
assert query_counts == {"NP-1": 19, "NP-2": 8, "NP-3": 8}
refs = read(paper / "references/list.json")
web = [row for row in refs["source_records"] if row["source_kind"] == "web_supplement"]
assert len(web) == 10
assert not any(row["title"] in report for row in web)
assert all(e["provenance"].get("evidence_type") != "web_supplement_evidence" for e in evidence.values())
output = {"status": "PASS", "cache_artifacts_verified": 9, "final_cards": 4,
          "all_final_cards_from_cache": True, "queries_in_report": query_counts,
          "web_source_records": len(web), "web_in_evidence_or_related_literature": False,
          "review_checkpoint_complete": True}
(base / "audit.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
print(json.dumps(output, ensure_ascii=False))
