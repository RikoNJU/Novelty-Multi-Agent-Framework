"""按论文组织的本地运行产物持久化。

当前实现面向开发和测试，把每篇论文的阶段产物写入
``outputs/<paper_id>/``。生产环境后续可替换为对象存储或数据库，但工作流
只应通过本模块写出产物，避免各节点自行拼接路径。
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import tempfile
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .schemas import (
    EvidenceCard,
    EvidenceReviewDecision,
    NoveltyPoint,
    NoveltyReport,
    PaperDocument,
    PaperInput,
    RejectedEvidence,
    ReferenceManifest,
    ReferenceReadResult,
    ResearchTask,
    SearchPlan,
    TaskResearchResult,
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
        workspace / "references" / "documents",
        workspace / "report",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    manifest_path = workspace / "references" / "list.json"
    if not manifest_path.exists():
        manifest = ReferenceManifest(
            subject_paper_id=paper_id,
            updated_at=datetime.now(timezone.utc),
        )
        _atomic_write_json(manifest_path, manifest.model_dump(mode="json"))
    return workspace


def reference_workspace(
    paper: PaperInput | PaperDocument | str,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """返回论文工作区内的参考文献目录，并确保其已经初始化。"""

    return paper_workspace(paper, output_root=output_root) / "references"


def reference_documents_dir(
    paper: PaperInput | PaperDocument | str,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """返回只能由持久化层生成的参考文献制品根目录。"""

    return reference_workspace(paper, output_root=output_root) / "documents"


def load_reference_manifest(
    paper: PaperInput | PaperDocument | str,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> ReferenceManifest:
    """读取并重新校验 references/list.json，不吞掉损坏数据。"""

    path = reference_workspace(paper, output_root=output_root) / "list.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ReferenceManifest.model_validate(payload)


def persist_reference_manifest(
    paper: PaperInput | PaperDocument | str,
    manifest: ReferenceManifest,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """校验并原子替换论文参考文献清单。"""

    paper_id = paper if isinstance(paper, str) else paper.paper_id
    if manifest.subject_paper_id != paper_id:
        raise ValueError(
            "manifest.subject_paper_id "
            f"{manifest.subject_paper_id!r} does not match paper_id {paper_id!r}"
        )
    validated = ReferenceManifest.model_validate(manifest.model_dump(mode="python"))
    path = reference_workspace(paper, output_root=output_root) / "list.json"
    _atomic_write_json(path, validated.model_dump(mode="json"))
    return path


class ReferenceStore:
    """参考文献 Manifest 与制品文件的单一工作区存储入口。"""

    def __init__(self, output_root: str | Path = DEFAULT_OUTPUTS_DIR) -> None:
        self.output_root = Path(output_root)

    def load_manifest(self, paper_id: str) -> ReferenceManifest:
        return load_reference_manifest(paper_id, output_root=self.output_root)

    def persist_manifest(
        self, paper_id: str, manifest: ReferenceManifest
    ) -> Path:
        return persist_reference_manifest(
            paper_id, manifest, output_root=self.output_root
        )

    def write_document(
        self,
        paper_id: str,
        *,
        work_id: str,
        artifact_id: str,
        extension: str,
        content: str,
    ) -> Path:
        """原子写入 UTF-8 文本制品，路径段只接受内部安全 ID。"""

        safe_work_id = _safe_storage_id(work_id, "work_id")
        safe_artifact_id = _safe_storage_id(artifact_id, "artifact_id")
        suffix = extension.strip().lower().lstrip(".")
        if not re.fullmatch(r"[a-z0-9]+", suffix):
            raise ValueError("artifact extension is unsafe")
        directory = reference_documents_dir(
            paper_id, output_root=self.output_root
        ) / safe_work_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{safe_artifact_id}.{suffix}"
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"artifact {artifact_id} content conflicts with existing file")
            return path
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=directory,
                prefix=f".{safe_artifact_id}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
            temporary_path = None
            return path
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def read_document_slice(
        self,
        paper_id: str,
        *,
        artifact_id: str,
        char_start: int,
        max_chars: int,
    ) -> ReferenceReadResult:
        """仅按 Manifest 中的文本 Artifact ID 读取受限字符片段。"""

        manifest = self.load_manifest(paper_id)
        artifact = next(
            (item for item in manifest.artifacts if item.artifact_id == artifact_id),
            None,
        )
        if artifact is None:
            raise ValueError(f"unknown artifact_id {artifact_id!r}")
        if artifact.media_type not in {
            "text/plain",
            "text/markdown",
            "text/html",
            "application/json",
        }:
            raise ValueError(
                f"artifact {artifact_id} media_type {artifact.media_type!r} is not readable text"
            )
        references_dir = reference_workspace(
            paper_id, output_root=self.output_root
        ).resolve()
        path = (references_dir / artifact.relative_path).resolve()
        if not path.is_relative_to(references_dir):
            raise ValueError(f"artifact {artifact_id} path escapes references workspace")
        if not path.is_file():
            raise FileNotFoundError(f"artifact {artifact_id} content file is missing")
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != artifact.sha256:
            raise ValueError(f"artifact {artifact_id} sha256 mismatch")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"artifact {artifact_id} is not valid UTF-8 text") from exc
        if char_start > len(text):
            raise ValueError(
                f"char_start {char_start} exceeds artifact {artifact_id} length"
            )
        char_end = min(len(text), char_start + max_chars)
        read_id = "read_" + hashlib.sha256(
            f"{artifact_id}\x1f{char_start}\x1f{char_end}\x1f{artifact.sha256}".encode()
        ).hexdigest()[:24]
        return ReferenceReadResult(
            read_id=read_id,
            work_id=artifact.work_id,
            artifact_id=artifact.artifact_id,
            role=artifact.role,
            char_start=char_start,
            char_end=char_end,
            text=text[char_start:char_end],
            has_more=char_end < len(text),
            sha256=artifact.sha256,
        )


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

    document.images = _copy_paper_images(document.images, input_dir / "images")
    paper.images = list(document.images)

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
        "images": [item.model_dump(mode="json") for item in document.images],
        "tables": [item.model_dump(mode="json") for item in document.tables],
        "equations": [item.model_dump(mode="json") for item in document.equations],
    }
    _write_json(input_dir / "content-list.json", content_list)
    _write_json(
        input_dir / "others" / "paper.json",
        paper.model_dump(mode="json"),
    )
    return workspace


def persist_workflow_input(
    paper: PaperInput,
    *,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """确保直接通过 JSON/API 启动的工作流也具备完整 paper-input 目录。"""

    workspace = paper_workspace(paper, output_root=output_root)
    input_dir = workspace / "paper-input"
    full_path = input_dir / "full.md"
    content_list_path = input_dir / "content-list.json"
    if not full_path.exists():
        full_path.write_text(paper.full_text + "\n", encoding="utf-8")
    if not content_list_path.exists():
        _write_json(
            content_list_path,
            {
                "paper_id": paper.paper_id,
                "title": paper.title,
                "source": paper.metadata.get("source", "workflow_input"),
                "page_count": int(paper.metadata.get("pages", "0") or 0),
                "sections": [],
                "keywords_zh": paper.keywords_zh,
                "keywords_en": paper.keywords_en,
                "reference_count": len(paper.references),
                "parse_warnings": [],
                "workflow_input": "others/paper.json",
                "images": [item.model_dump(mode="json") for item in paper.images],
                "tables": [item.model_dump(mode="json") for item in paper.tables],
                "equations": [
                    item.model_dump(mode="json") for item in paper.equations
                ],
            },
        )
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
    search_plans: Sequence[SearchPlan] = (),
    executed_queries: Sequence[Mapping[str, Any]] = (),
    rounds: int,
    point_order: Sequence[str] = (),
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """按查新点写出任务、语义计划及真正执行的数据库 Query。"""

    workspace = paper_workspace(paper, output_root=output_root)
    path = workspace / "retrieval-plans.json"
    grouped: dict[str, list[ResearchTask]] = {}
    for task in tasks:
        grouped.setdefault(task.novelty_point_id, []).append(task)
    grouped_plans: dict[str, list[SearchPlan]] = {}
    for plan in search_plans:
        grouped_plans.setdefault(plan.novelty_point_id, []).append(plan)
    grouped_queries: dict[str, list[Mapping[str, Any]]] = {}
    for query in executed_queries:
        point_id = str(query.get("novelty_point_id", ""))
        grouped_queries.setdefault(point_id, []).append(query)

    ordered_point_ids = list(
        dict.fromkeys([*point_order, *grouped, *grouped_plans, *grouped_queries])
    )
    plans = []
    for sequence, point_id in enumerate(ordered_point_ids, start=1):
        point_tasks = grouped.get(point_id, [])
        point_plans = grouped_plans.get(point_id, [])
        point_queries = grouped_queries.get(point_id, [])
        plans.append(
            {
                "sequence": sequence,
                "novelty_point_id": point_id,
                "research_tasks": [
                    task.model_dump(mode="json") for task in point_tasks
                ],
                "search_plans": [
                    plan.model_dump(mode="json") for plan in point_plans
                ],
                "executed_queries": [dict(query) for query in point_queries],
                "query_plan": {
                    "queries": _unique(
                        str(query.get("query", "")) for query in point_queries
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
    validator_accepted_cards: Sequence[EvidenceCard] | None = None,
    review_decisions: Sequence[EvidenceReviewDecision] | None = None,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """写出证据校验前后结果，保留拒绝原因供审计。"""

    workspace = paper_workspace(paper, output_root=output_root)
    path = workspace / "evidence-cards.json"
    payload: dict[str, Any] = {
        "paper_id": paper.paper_id,
        "raw_evidence_cards": [card.model_dump(mode="json") for card in raw_cards],
        "accepted_evidence_cards": [
            card.model_dump(mode="json") for card in accepted_cards
        ],
        "rejected_evidence": [
            item.model_dump(mode="json") for item in rejected_evidence
        ],
    }
    if validator_accepted_cards is not None:
        payload["validator_accepted_cards"] = [
            card.model_dump(mode="json") for card in validator_accepted_cards
        ]
    if review_decisions is not None:
        payload["review_decisions"] = [
            decision.model_dump(mode="json") for decision in review_decisions
        ]
    _write_json(path, payload)
    return path


def persist_task_research_result(
    paper_id: str,
    result: TaskResearchResult,
    *,
    attempt: int,
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """写出单任务审计，不包含全文或模型隐式推理。"""

    workspace = paper_workspace(paper_id, output_root=output_root)
    point_id = _safe_storage_id(result.novelty_point_id, "novelty_point_id")
    task_id = _safe_storage_id(result.task_id, "task_id")
    directory = workspace / "research-runs" / point_id / task_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"attempt-{attempt}.json"
    _atomic_write_json(path, result.model_dump(mode="json"))
    return path


def persist_task_retrieval_audit(
    paper: PaperInput,
    tasks: Sequence[ResearchTask],
    results: Sequence[TaskResearchResult],
    *,
    rounds: int,
    point_order: Sequence[str] = (),
    output_root: str | Path = DEFAULT_OUTPUTS_DIR,
) -> Path:
    """从任务结果聚合真实 SearchExecution，保留旧 retrieval-plans 文件。"""

    task_by_key = {(task.novelty_point_id, task.task_id): task for task in tasks}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        key = (result.novelty_point_id, result.task_id)
        task = task_by_key.get(key)
        for bundle in result.research_bundles:
            for execution in bundle.search_executions:
                grouped.setdefault(result.novelty_point_id, []).append(
                    {
                        "database": execution.source_id,
                        "task_id": result.task_id,
                        "novelty_point_id": result.novelty_point_id,
                        "strategy_id": execution.parameters.get("strategy_id", ""),
                        "level": execution.parameters.get("level", ""),
                        "query": execution.query,
                        "status": execution.status.value,
                        "results": [
                            item.model_dump(mode="json") for item in execution.results
                        ],
                    }
                )
        if task is not None:
            grouped.setdefault(result.novelty_point_id, [])
    ordered = list(dict.fromkeys([*point_order, *grouped]))
    plans = []
    for sequence, point_id in enumerate(ordered, start=1):
        point_tasks = [task for task in tasks if task.novelty_point_id == point_id]
        executed = grouped.get(point_id, [])
        plans.append(
            {
                "sequence": sequence,
                "novelty_point_id": point_id,
                "research_tasks": [
                    task.model_dump(mode="json") for task in point_tasks
                ],
                "search_plans": [],
                "executed_queries": executed,
                "query_plan": {
                    "queries": _unique(item["query"] for item in executed),
                    "attempts": sorted({task.attempt for task in point_tasks}),
                },
            }
        )
    path = paper_workspace(paper, output_root=output_root) / "retrieval-plans.json"
    _atomic_write_json(
        path,
        {
            "paper_id": paper.paper_id,
            "rounds": rounds,
            "novelty_point_plans": plans,
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


def _copy_paper_images(
    images: Sequence[Any],
    dest_dir: Path,
) -> list[Any]:
    """把 MinerU 产物图片复制到 paper 工作区，并返回路径已更新的图片列表。"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    updated: list[Any] = []
    for index, image in enumerate(images):
        src = Path(image.path)
        if src.exists() and src.is_file():
            dest_name = f"{index:03d}_{src.name}"
            dest = dest_dir / dest_name
            shutil.copy2(src, dest)
            updated.append(image.model_copy(update={"path": f"images/{dest_name}"}))
        else:
            updated.append(image)
    return updated


def _safe_directory_name(paper_id: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", paper_id.strip()).strip("._")
    if not name:
        raise ValueError("paper_id 无法转换为安全的工作目录名")
    return name


def _safe_storage_id(value: str, field_name: str) -> str:
    value = value.strip()
    if not value or re.fullmatch(r"[A-Za-z0-9_-]+", value) is None:
        raise ValueError(f"{field_name} is not a safe storage identifier")
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _atomic_write_json(path: Path, payload: Any) -> None:
    """在目标目录落盘后原子替换 JSON，并清理失败的临时文件。"""

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))
