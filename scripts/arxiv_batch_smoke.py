#!/usr/bin/env python3
"""Run ARXIV-BATCH-01 A/B/D/C smoke and optionally write its JSON artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT_ROOT), str(PROJECT_ROOT / "backend" / "src")]

from novelty_agent_framework.experiments.arxiv_batch_smoke import run_batch_smoke
from novelty_agent_framework.tools.database_search.providers.arxiv_scheduler import (
    ArxivRequestScheduler,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-interval", type=float, default=4.0)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-retries", type=int, default=1)
    args = parser.parse_args()
    scheduler = ArxivRequestScheduler(
        min_interval=args.min_interval,
        timeout=args.timeout,
        max_retries=args.max_retries,
        metadata_batch_window_ms=200,
        metadata_batch_max_size=32,
    )
    try:
        result = run_batch_smoke(scheduler=scheduler)
    finally:
        scheduler.shutdown()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if args.output.is_file():
            previous = json.loads(args.output.read_text(encoding="utf-8"))
            history = list(previous.get("attempt_history", []))
            history.append(
                {
                    "provider_access": previous.get("provider_access"),
                    "cases": [
                        {
                            key: case.get(key)
                            for key in ("case", "classification", "http_status", "error_type")
                            if key in case
                        }
                        for case in previous.get("cases", [])
                    ],
                    "scheduler_metrics": {
                        key: previous.get("scheduler_metrics", {}).get(key)
                        for key in (
                            "physical_api_requests",
                            "http_200_count",
                            "http_429_count",
                            "read_timeout_count",
                            "interval_violation_count",
                        )
                    },
                }
            )
        result["attempt_history"] = history
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["provider_access"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
