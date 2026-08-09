"""按论文组织的本地运行产物持久化。

当前实现面向开发和测试，把每篇论文的阶段产物写入
``outputs/<paper_id>/``。生产环境后续可替换为对象存储或数据库，但工作流
只应通过本模块写出产物，避免各节点自行拼接路径。
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Sequence

from .schemas import (
    EvidenceCard,
    NoveltyPoint,
    NoveltyReport,
    PaperDocument,
    PaperInput,
    RejectedEvidence,
    ResearchTask,
)

DEFAULT_OUTPUTS_DIR = Path("outputs")
STORAGE_VERSION = "test-version-local-file"


def paper_workspace(
    paper: PaperInput | PaperDocument | str,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """创建并返回单篇论文工作目录，阻止 paper_id 逃逸输出根目录。"""

    paper_id = paper if isinstance(paper, str) else paper.paper_id
    safe_name = _safe_directory_name(paper_id)
    workspace = Path(output_root) / safe_name
    for directory in (
        workspace / "paper-input" / "images",
        workspace / "paper-input" / "others",
        workspace / "report",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return workspace


def persist_paper_input(
    document: PaperDocument,
    paper: PaperInput,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """写出论文全文、内容清单和供工作流重载的结构化输入。"""

    workspace = paper_workspace(document, output_root=output_root)
    input_dir = workspace / "paper-input"
    (input_dir / "full.md").write_text(document.full_text + "\n", encoding="utf-8")

    content_list = {
        "paper_id": document.paper_id,
        "title": document.title,
        "source": document.source,
        "page_count": len(document.pages),
        "sections": [
            {
                "name": name,
                "present": bool(content.strip()),
                "characters": len(content),
            }
            for name, content in document.sections.items()
        ],
        "keywords_zh": document.keywords_zh,
        "keywords_en": document.keywords_en,
        "reference_count": len(document.references),
        "parse_warnings": document.parse_warnings,
        "workflow_input": "others/paper.json",
    }
    _write_json(input_dir / "content-list.json", content_list)
    _write_json(
        input_dir / "others" / "paper.json",
        paper.model_dump(mode="json"),
    )
    return workspace


def persist_novelty_points(
    paper: PaperInput,
    points: Sequence[NoveltyPoint],
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """把生成的查新点写入论文工作目录。"""

    workspace = paper_workspace(paper, output_root=output_root)
    path = workspace / "novelty-points.json"
    _write_json(
        path,
        {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "storage": STORAGE_VERSION,
            "novelty_points": [point.model_dump(mode="json") for point in points],
        },
    )
    return path


def persist_retrieval_plans(
    paper: PaperInput,
    tasks: Sequence[ResearchTask],
    *,
    rounds: int,
    point_order: Sequence[str] = (),
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """按查新点顺序写出 ResearchTask 及汇总 QueryPlan。"""

    workspace = paper_workspace(paper, output_root=output_root)
    path = workspace / "retrieval-plans.json"
    grouped: dict[str, list[ResearchTask]] = {}
    for task in tasks:
        grouped.setdefault(task.novelty_point_id, []).append(task)

    ordered_point_ids = list(dict.fromkeys([*point_order, *grouped]))
    plans = []
    for sequence, point_id in enumerate(ordered_point_ids, start=1):
        point_tasks = grouped.get(point_id, [])
        plans.append(
            {
                "sequence": sequence,
                "novelty_point_id": point_id,
                "research_tasks": [
                    task.model_dump(mode="json") for task in point_tasks
                ],
                "query_plan": {
                    "queries": _unique(
                        query for task in point_tasks for query in task.queries
                    ),
                    "candidate_document_ids": _unique(
                        document_id
                        for task in point_tasks
                        for document_id in task.candidate_document_ids
                    ),
                    "attempts": sorted({task.attempt for task in point_tasks}),
                },
            }
        )
    _write_json(
        path,
        {
            "paper_id": paper.paper_id,
            "rounds": rounds,
            "novelty_point_plans": plans,
        },
    )
    return path


def persist_evidence_cards(
    paper: PaperInput,
    *,
    raw_cards: Sequence[EvidenceCard],
    accepted_cards: Sequence[EvidenceCard],
    rejected_evidence: Sequence[RejectedEvidence],
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """写出证据校验前后结果，保留拒绝原因供审计。"""

    workspace = paper_workspace(paper, output_root=output_root)
    path = workspace / "evidence-cards.json"
    _write_json(
        path,
        {
            "paper_id": paper.paper_id,
            "raw_evidence_cards": [card.model_dump(mode="json") for card in raw_cards],
            "accepted_evidence_cards": [
                card.model_dump(mode="json") for card in accepted_cards
            ],
            "rejected_evidence": [
                item.model_dump(mode="json") for item in rejected_evidence
            ],
        },
    )
    return path


def persist_report(
    paper: PaperInput,
    report: NoveltyReport,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """写出 Coordinator.synthesize() 生成并通过校验的结构化报告。"""

    workspace = paper_workspace(paper, output_root=output_root)
    path = workspace / "report.json"
    _write_json(path, report.model_dump(mode="json"))
    return path


def _safe_directory_name(paper_id: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", paper_id.strip()).strip("._")
    if not name:
        raise ValueError("paper_id 无法转换为安全的工作目录名")
    return name


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))
