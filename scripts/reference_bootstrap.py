#!/usr/bin/env python3
"""Run deterministic reference bootstrap for one persisted PaperInput."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "src"))

from novelty_agent_framework.persistence import SubjectReferenceStore, paper_workspace
from novelty_agent_framework.processing.reference_bootstrap import ReferenceBootstrapService, ReferenceProviderRegistry
from novelty_agent_framework.schemas import PaperInput, ResolutionStatus
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivSearchTool


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--paper-id", required=True)
    result.add_argument("--output-root", default="outputs")
    result.add_argument("--force", action="store_true")
    result.add_argument("--retry-failed", action="store_true")
    result.add_argument("--max-concurrency", type=int, default=4)
    result.add_argument("--provider", choices=("arxiv",))
    result.add_argument("--dry-run", action="store_true")
    return result


async def run(args: argparse.Namespace) -> int:
    root = Path(args.output_root)
    paper_path = paper_workspace(args.paper_id, output_root=root) / "paper-input" / "others" / "paper.json"
    paper = PaperInput.model_validate(json.loads(paper_path.read_text(encoding="utf-8")))
    registry = ReferenceProviderRegistry([] if args.dry_run else [ArxivSearchTool()])
    service = ReferenceBootstrapService(registry, SubjectReferenceStore(root), max_concurrency=args.max_concurrency)
    manifest = await service.bootstrap(paper.paper_id, paper.references, force=args.force, retry_failed=args.retry_failed, provider=args.provider, dry_run=args.dry_run)
    counts = {status.value: sum(entry.resolution_status == status for entry in manifest.entries) for status in ResolutionStatus}
    print(json.dumps({"paper_id": paper.paper_id, "total": len(manifest.entries), "bootstrap_ready": manifest.bootstrap_ready, **counts}, ensure_ascii=False))
    return 0 if manifest.bootstrap_ready else 1


def main() -> int:
    try:
        return asyncio.run(run(parser().parse_args()))
    except Exception as exc:
        print(f"reference bootstrap failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
