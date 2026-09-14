"""Run the standard PaperInput workflow in a numbered isolated workspace.

Example:
    python scripts/run_full_workflow_live.py \
        --paper-json outputs/MG19333vrw/paper-input/others/paper.json \
        --runs-root outputs/runs --run-number 4 \
        --max-rounds 1 --max-concurrency 4
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import (
    build_standard_full_workflow,
    load_application_config,
)
from novelty_agent_framework.core.run_identity import file_run_identity
from novelty_agent_framework.processing import prepare_paper_input_references
from novelty_agent_framework.schemas import PaperInput

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--paper-json", required=True, type=Path)
    result.add_argument("--runs-root", type=Path, default=Path("outputs/runs"))
    result.add_argument("--run-number", type=int)
    result.add_argument("--max-rounds", type=int, default=1)
    result.add_argument("--max-concurrency", type=int, default=1)
    result.add_argument("--force-reference-bootstrap", action="store_true")
    return result


def allocate_run_directory(
    runs_root: str | Path, run_number: int | None = None
) -> tuple[int, Path]:
    """Atomically reserve a pure-numeric run directory without overwriting."""

    root = Path(runs_root)
    root.mkdir(parents=True, exist_ok=True)
    if run_number is not None:
        if run_number < 1:
            raise ValueError("run-number must be positive")
        path = root / f"{run_number:04d}"
        path.mkdir(exist_ok=False)
        return run_number, path

    existing = [
        int(item.name)
        for item in root.iterdir()
        if item.is_dir() and item.name.isdigit()
    ]
    candidate = max(existing, default=0) + 1
    while True:
        path = root / f"{candidate:04d}"
        try:
            path.mkdir(exist_ok=False)
        except FileExistsError:
            candidate += 1
            continue
        return candidate, path


def main() -> None:
    _load_dev_env()
    args = parser().parse_args()
    paper_json = args.paper_json.resolve(strict=True)
    paper = PaperInput.model_validate_json(paper_json.read_text(encoding="utf-8"))
    run_number, run_dir = allocate_run_directory(args.runs_root, args.run_number)
    run_dir = run_dir.resolve()
    identity = file_run_identity("paper_input", paper_json, project_root=PROJECT_ROOT)
    identity["run_number"] = run_number
    started_at = datetime.now(UTC)
    monotonic_started = time.monotonic()
    run_manifest: dict[str, Any] = {
        "run_number": run_number,
        "status": "RUNNING",
        "entrypoint": "paper_input",
        "paper_id": paper.paper_id,
        "paper_json_source": identity["input_identity"]["paper_json"],
        "paper_sha256": identity["input_identity"]["paper_sha256"],
        "git_commit": _git_commit(),
        "max_rounds": args.max_rounds,
        "max_concurrency": args.max_concurrency,
        "started_at": started_at.isoformat(),
    }
    manifest_path = run_dir / "run.json"
    _write_json(manifest_path, run_manifest)

    workflow = None
    try:
        config = load_application_config()
        config.project.workflow.max_rounds = args.max_rounds
        config.project.workflow.max_concurrency = args.max_concurrency
        workflow = build_standard_full_workflow(config, output_root=run_dir)
        stable_root = _stable_output_root(paper_json, paper.paper_id)
        prepare_paper_input_references(
            paper,
            stable_output_root=stable_root,
            run_output_root=run_dir,
            force=args.force_reference_bootstrap,
            max_concurrency=args.max_concurrency,
        )
        result = workflow.run(paper, run_identity=identity)
        payload = json.loads(result.model_dump_json())
        result_path = run_dir / "result.json"
        _write_json(result_path, payload)
    except KeyboardInterrupt as exc:
        _finish_manifest(
            run_manifest,
            manifest_path,
            status="INTERRUPTED",
            started=monotonic_started,
            workflow=workflow,
            error=exc,
        )
        raise
    except BaseException as exc:
        _finish_manifest(
            run_manifest,
            manifest_path,
            status="FAILED",
            started=monotonic_started,
            workflow=workflow,
            error=exc,
        )
        raise
    else:
        _finish_manifest(
            run_manifest,
            manifest_path,
            status="SUCCESS",
            started=monotonic_started,
            workflow=workflow,
            result_path=result_path,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def _stable_output_root(paper_json: Path, paper_id: str) -> Path:
    """Recognize the canonical outputs/<paper_id>/paper-input/others path."""

    if (
        paper_json.parent.name == "others"
        and paper_json.parent.parent.name == "paper-input"
        and paper_json.parent.parent.parent.name == paper_id
    ):
        return paper_json.parent.parent.parent.parent
    return Path("outputs").resolve()


def _finish_manifest(
    manifest: dict[str, Any],
    path: Path,
    *,
    status: str,
    started: float,
    workflow: Any,
    result_path: Path | None = None,
    error: BaseException | None = None,
) -> None:
    manifest.update(
        {
            "status": status,
            "finished_at": datetime.now(UTC).isoformat(),
            "duration": round(time.monotonic() - started, 6),
            "runtime_run_id": getattr(workflow, "last_runtime_run_id", None),
            "result_path": str(result_path) if result_path is not None else None,
            "rendered_report_path": getattr(
                workflow, "last_rendered_report_path", None
            ),
        }
    )
    if error is not None:
        manifest["error"] = f"{type(error).__name__}: {error}"[:1000]
    _write_json(path, manifest)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


if __name__ == "__main__":
    main()
