"""对指定论文跑完整正式工作流（真实模型 live）。

用法：
    python scripts/run_full_workflow_live.py \
        --paper-json outputs/MG19333vrw/paper-input/others/paper.json \
        --output outputs/MG19333vrw/full-workflow-live.json \
        --max-rounds 1 --max-concurrency 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import build_workflow, load_application_config
from novelty_agent_framework.core.run_identity import file_run_identity
from novelty_agent_framework.schemas import PaperInput

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    _load_dev_env()
    parser = argparse.ArgumentParser(description="完整正式工作流 live 运行")
    parser.add_argument("--paper-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-rounds", type=int, default=1)
    parser.add_argument("--max-concurrency", type=int, default=1)
    args = parser.parse_args()

    config = load_application_config()
    config.project.workflow.max_rounds = args.max_rounds
    config.project.workflow.max_concurrency = args.max_concurrency
    workflow = build_workflow(config)

    paper_json = args.paper_json.resolve(strict=True)
    paper = PaperInput.model_validate_json(paper_json.read_text(encoding="utf-8"))
    result = workflow.run(
        paper,
        run_identity=file_run_identity(
            "paper_input", paper_json, project_root=PROJECT_ROOT
        ),
    )
    payload = json.loads(result.model_dump_json())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
