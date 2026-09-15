"""A/B/D/C live smoke for the process-wide arXiv scheduler experiment."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .arxiv_rate_smoke import DEFAULT_CASES, probe_case
from ..tools.database_search.providers.arxiv import (
    ArxivMetadataTool,
    ArxivSearchTool,
)
from ..tools.database_search.providers.arxiv_scheduler import ArxivRequestScheduler


KNOWN_METADATA_IDS = (
    "1706.03762",
    "1810.04805",
    "2005.14165",
    "2103.00020",
    "2203.02155",
    "2302.13971",
    "2307.09288",
    "2310.06825",
    "2403.08295",
    "2407.21783",
)


def run_batch_smoke(
    *,
    scheduler: ArxivRequestScheduler,
) -> dict[str, Any]:
    search = ArxivSearchTool(scheduler=scheduler)
    metadata = ArxivMetadataTool(scheduler=scheduler)
    a = probe_case(search, DEFAULT_CASES[0])
    b = (
        probe_case(search, DEFAULT_CASES[1])
        if a["classification"] == "VALID_HIT"
        else _skipped("B", "exact_english_title")
    )
    d: dict[str, Any]
    if b["classification"] == "VALID_HIT":
        try:
            with ThreadPoolExecutor(max_workers=len(KNOWN_METADATA_IDS)) as executor:
                values = list(executor.map(metadata.resolve, KNOWN_METADATA_IDS))
            resolved = sum(value is not None for value in values)
            d = {
                "case": "D",
                "purpose": "metadata_batch",
                "requested_ids": list(KNOWN_METADATA_IDS),
                "resolved_count": resolved,
                "classification": (
                    "VALID_HIT" if resolved == len(KNOWN_METADATA_IDS) else "PARTIAL_MISSING"
                ),
            }
        except Exception as exc:
            d = {
                "case": "D",
                "purpose": "metadata_batch",
                "requested_ids": list(KNOWN_METADATA_IDS),
                "classification": "PROVIDER_ACCESS_FAILURE",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
    else:
        d = _skipped("D", "metadata_batch")
    c = (
        probe_case(search, DEFAULT_CASES[2])
        if d["classification"] == "VALID_HIT"
        else _skipped("C", "run_d_structured_query")
    )
    cases = [a, b, d, c]
    return {
        "check": "ARXIV-BATCH-01",
        "provider_access": (
            "PASS"
            if all(item["classification"] == "VALID_HIT" for item in (a, b, d))
            else "FAIL"
        ),
        "execution_order": ["A", "B", "D", "C"],
        "cases": cases,
        "scheduler_metrics": scheduler.snapshot_metrics(include_events=True),
    }


def _skipped(case_id: str, purpose: str) -> dict[str, Any]:
    return {
        "case": case_id,
        "purpose": purpose,
        "classification": "SKIPPED_UPSTREAM_GATE",
    }


__all__ = ["KNOWN_METADATA_IDS", "run_batch_smoke"]
