"""Verify the published implementation without models, providers or local outputs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
inventory = json.loads((OUT / "source_inventory.json").read_text())
mismatches = [name for name, expected in inventory["files"].items()
              if not (ROOT / name).is_file()
              or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected]
print(json.dumps({"files_checked": len(inventory["files"]), "mismatches": mismatches,
                  "task_acceptance": "not_accepted"}, ensure_ascii=False))
raise SystemExit(bool(mismatches))
