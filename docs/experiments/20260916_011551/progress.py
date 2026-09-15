"""Read live audit artifacts; no external requests."""
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent / "run"
def read(path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default

stages = [(p.parent.name, read(p, {})) for p in sorted(root.glob("*/runtime/*/stages/*/meta.json"))]
models = read(root / "model_calls.json", [])
http = []
if (root / "http_events.jsonl").exists():
    for line in (root / "http_events.jsonl").read_text().splitlines():
        try:
            http.append(json.loads(line))
        except ValueError:
            pass
print(json.dumps({
    "status": read(root / "run.json", {}).get("status"),
    "stages": [(name, row.get("status"), row.get("duration")) for name, row in stages[-8:]],
    "model_calls": len(models),
    "models_by_stage": dict(Counter(row.get("stage") for row in models)),
    "http": dict(Counter(f"{row['host']}:{row['status']}" for row in http)),
    "review_checkpoint": read(root / "MF2033k6lC/novelty-reviews.json", {}).get("phase"),
}, ensure_ascii=False))
