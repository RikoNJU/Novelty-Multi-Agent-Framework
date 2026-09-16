"""Archive the completed repeat and verify external evidence against Reader text."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
BASE = Path(__file__).resolve().parent
RAW = ROOT / "outputs" / BASE.name
RUN = RAW / "runtime/full"
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src")]
from novelty_agent_framework.tools.evidence_card_builder import _quote_matches

manifest = json.loads((RUN / "run.json").read_text())
assert manifest["status"] == "SUCCESS", manifest
final = json.loads((RUN / "result.json").read_text())
refs = json.loads((RUN / "MF2033k6lC/references/list.json").read_text())
records = {r["source_record_id"]: r for r in refs["source_records"]}
retained = {c["card_id"] for c in final["evidence_cards"]}
proof, warnings = [], []
for path in sorted(RUN.glob("MF*/runtime/*/stages/*run_research_task/output.json")):
    for task in json.loads(path.read_text()).get("task_research_results", []):
        warnings.append({"stage": str(path.relative_to(RUN)),
                         "point": task["novelty_point_id"], "task": task["task_id"],
                         "status": task["status"], "warnings": task["warnings"]})
        evidence = {e["evidence_id"]: e for e in task["evidence"]}
        reads = {r["read_id"]: r for r in task["read_results"]}
        for card in task["evidence_cards"]:
            bindings = []
            for eid in card["evidence_ids"]:
                item = evidence[eid]
                p = item["provenance"]
                if p["artifact_namespace"] != "research_reference":
                    continue
                record = records[p["source_record_id"]]
                read = reads[p["read_id"]]
                assert record["raw_metadata"]["channel"] == "arxiv-web-search"
                assert _quote_matches(item["quote"], read["text"])
                bindings.append({"evidence_id": eid, "source_url": record["landing_url"],
                                 "channel": record["raw_metadata"]["channel"],
                                 "read_id": read["read_id"], "read_sha256": read["sha256"],
                                 "quote_matches_builder_rules": True})
            if bindings:
                proof.append({"card_id": card["card_id"], "point": card["novelty_point_id"],
                              "title": card["document_title"], "retained": card["card_id"] in retained,
                              "bindings": bindings})
for name, data in [("web-card-provenance.json", proof), ("task-warnings.json", warnings)]:
    (BASE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
files = [RUN / "run.json", RUN / "result.json", *RUN.glob("MF*/runtime/*/summary.json"),
         Path(manifest["rendered_report_path"])]
for src in files:
    shutil.copy2(src, BASE / src.name)
hashes = [{"path": str(p.relative_to(RAW)), "bytes": p.stat().st_size,
           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
          for p in sorted(RAW.rglob("*")) if p.is_file()]
(BASE / "raw-manifest.json").write_text(json.dumps(hashes, ensure_ascii=False, indent=2) + "\n")
print(f"Archived {len(files)} outputs; verified {len(proof)} external cards; hashed {len(hashes)} raw files.")
