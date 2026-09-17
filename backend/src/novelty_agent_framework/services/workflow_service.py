"""论文查新任务的 Web 应用服务。"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from novelty_agent_framework.config import (
    NoveltyWebSettings,
    build_model_registry,
    build_standard_full_workflow,
    load_application_config,
)
from novelty_agent_framework.schemas import PaperInput
from novelty_agent_framework.services.jobs import (
    InMemoryRunStore,
    RunError,
    RunReport,
    RunSnapshot,
    RunStage,
)
from novelty_agent_framework.workflows import NoveltyWorkflow

logger = logging.getLogger(__name__)
WorkflowFactory = Callable[[Path], NoveltyWorkflow]

_INTERNAL_STAGE_MAP = {
    "extract_points": RunStage.EXTRACT_POINTS,
    "plan": RunStage.PLAN_RESEARCH,
    "dispatch_planning_tasks": RunStage.PLAN_RESEARCH,
    "plan_research_task": RunStage.PLAN_RESEARCH,
    "dispatch_research_tasks": RunStage.RESEARCH,
    "run_research_task": RunStage.RESEARCH,
    "validate_evidence": RunStage.VALIDATE_EVIDENCE,
    "review_evidence": RunStage.VALIDATE_EVIDENCE,
    "validate_synthesis_input": RunStage.VALIDATE_EVIDENCE,
    "check_final_evidence_sufficiency": RunStage.VALIDATE_EVIDENCE,
    "plan_supplement": RunStage.VALIDATE_EVIDENCE,
    "synthesize_report": RunStage.RENDER_REPORT,
    "validate_report_integrity": RunStage.RENDER_REPORT,
    "persist_report": RunStage.RENDER_REPORT,
    "render_report": RunStage.RENDER_REPORT,
}


class WorkflowConfigurationError(RuntimeError):
    """真实工作流无法安全启动。"""


class UploadValidationError(ValueError):
    def __init__(self, code: str, message: str, *, status_code: int = 422) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class NoveltyWorkflowService:
    def __init__(
        self,
        *,
        workflow_factory: WorkflowFactory,
        runs_root: str | Path,
        processor: Any | None = None,
        store: InMemoryRunStore | None = None,
        max_upload_bytes: int = 30 * 1024 * 1024,
    ) -> None:
        self.workflow_factory = workflow_factory
        self.processor = processor
        self.store = store or InMemoryRunStore()
        self.runs_root = Path(runs_root).resolve()
        self.max_upload_bytes = max_upload_bytes
        self.runs_root.mkdir(parents=True, exist_ok=True)
        (self.runs_root / ".uploads").mkdir(exist_ok=True)

    def create_run(self) -> RunSnapshot:
        snapshot = self.store.create()
        self._run_dir(snapshot.task_id).mkdir(parents=True, exist_ok=False)
        return snapshot

    async def create_file_run(self, upload: UploadFile) -> tuple[RunSnapshot, Path]:
        self._validate_upload_metadata(upload)
        temporary_path: Path | None = None
        try:
            descriptor, raw_path = tempfile.mkstemp(
                prefix="paper-", suffix=".upload", dir=self.runs_root / ".uploads"
            )
            os.close(descriptor)
            temporary_path = Path(raw_path)
            total = 0
            first_kib = bytearray()
            with temporary_path.open("wb") as destination:
                while chunk := await upload.read(1024 * 1024):
                    total += len(chunk)
                    if total > self.max_upload_bytes:
                        raise UploadValidationError(
                            "file_too_large",
                            "论文文件超过服务端大小限制。",
                            status_code=413,
                        )
                    if len(first_kib) < 1024:
                        first_kib.extend(chunk[: 1024 - len(first_kib)])
                    destination.write(chunk)
            if total == 0:
                raise UploadValidationError("empty_file", "不能上传空文件。")
            if b"%PDF-" not in bytes(first_kib):
                raise UploadValidationError(
                    "invalid_pdf_signature", "文件内容不是有效的 PDF。"
                )

            snapshot = self.create_run()
            input_dir = self._run_dir(snapshot.task_id) / "input"
            input_dir.mkdir()
            destination = input_dir / "paper.pdf"
            os.replace(temporary_path, destination)
            temporary_path = None
            return snapshot, destination
        finally:
            await upload.close()
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    async def execute(self, task_id: str, paper: PaperInput) -> None:
        self.store.mark_running(task_id, stage=RunStage.EXTRACT_POINTS)
        await self._execute_workflow(task_id, paper)

    async def execute_file(self, task_id: str, path: Path) -> None:
        self.store.mark_running(task_id, stage=RunStage.PARSE_PAPER)
        if self.processor is None:
            self.store.mark_failed(
                task_id,
                RunError(
                    code="paper_processing_unavailable",
                    message="论文解析服务尚未正确配置。",
                    retryable=False,
                ),
            )
            return
        try:
            document = await asyncio.to_thread(
                self.processor.process, path, paper_id=task_id
            )
            paper = self.processor.to_paper_input(document)
        except Exception:  # noqa: BLE001 - public errors must be normalized
            logger.exception("paper parsing failed for task %s", task_id)
            self.store.mark_failed(
                task_id,
                RunError(
                    code="paper_parse_failed",
                    message="论文解析失败，请确认 PDF 可正常打开且包含可识别内容。",
                    retryable=False,
                ),
            )
            return
        await self._execute_workflow(task_id, paper)

    async def _execute_workflow(self, task_id: str, paper: PaperInput) -> None:
        run_dir = self._run_dir(task_id)
        workflow = self.workflow_factory(run_dir)

        def progress(stage: str, round: int | None) -> None:
            mapped = _INTERNAL_STAGE_MAP.get(stage)
            if mapped is not None:
                self.store.mark_progress(task_id, mapped, round=round)

        try:
            result = await workflow.arun(paper, progress_callback=progress)
            rendered = workflow.last_rendered_report_path
            report_path = Path(rendered).resolve() if rendered else None
            if (
                report_path is None
                or not report_path.is_file()
                or not report_path.is_relative_to(run_dir.resolve())
            ):
                raise RuntimeError("workflow completed without a task-scoped report")
            base_url = f"/api/novelty/runs/{task_id}/report"
            report = RunReport(
                available_formats=["md"],
                preview_url=f"{base_url}?disposition=inline",
                downloads={"md": f"{base_url}?disposition=attachment"},
            )
            self.store.mark_succeeded(
                task_id,
                result.model_dump(mode="json"),
                report=report,
                report_path=report_path,
            )
        except Exception:  # noqa: BLE001 - public errors must be normalized
            logger.exception("novelty workflow failed for task %s", task_id)
            self.store.mark_failed(
                task_id,
                RunError(
                    code="workflow_failed",
                    message="查新工作流未能完成，请稍后重新提交或联系服务管理员。",
                    retryable=True,
                ),
            )

    def get_run(self, task_id: str) -> RunSnapshot | None:
        return self.store.get(task_id)

    def get_report(self, task_id: str) -> tuple[Path, str] | None:
        snapshot = self.store.get(task_id)
        path = self.store.get_report_path(task_id)
        if snapshot is None or snapshot.report is None or path is None or not path.is_file():
            return None
        return path, f"{task_id}-查新报告.md"

    def _run_dir(self, task_id: str) -> Path:
        path = (self.runs_root / task_id).resolve()
        if not path.is_relative_to(self.runs_root):
            raise ValueError("unsafe task id")
        return path

    @staticmethod
    def _validate_upload_metadata(upload: UploadFile) -> None:
        filename = upload.filename or ""
        if Path(filename).suffix.lower() != ".pdf":
            raise UploadValidationError("unsupported_file_type", "论文原文仅支持 PDF。")
        if upload.content_type and upload.content_type not in {
            "application/pdf",
            "application/octet-stream",
        }:
            raise UploadValidationError(
                "mime_mismatch", "文件类型与扩展名不符，请重新选择。"
            )


def build_real_workflow_service(settings: NoveltyWebSettings) -> NoveltyWorkflowService:
    """构建真实 Web 工作流，并在接收任务前验证关键运行条件。"""

    config = load_application_config()
    if config.reviewer is None or not config.reviewer.enabled:
        raise WorkflowConfigurationError("真实工作流必须启用 Reviewer")
    database = config.researcher.tools.database_search
    active_provider = database.providers.get(database.active_source)
    if not active_provider or not active_provider.get("enabled", False):
        raise WorkflowConfigurationError(
            f"真实工作流的数据源 {database.active_source!r} 未启用"
        )
    registry = build_model_registry(config)
    aliases = {
        config.researcher.model.alias,
        config.search_planner.model.alias,
        config.coordinator.model.alias,
        config.point_extractor.model.alias,
    }
    if config.reviewer and config.reviewer.enabled:
        aliases.add(config.reviewer.model.alias)
    processing = config.project.processing
    aliases.update(
        alias
        for alias in (processing.get("ocr_model"), processing.get("llm_model"))
        if alias
    )
    missing = sorted(
        alias
        for alias in aliases
        if not getattr(getattr(registry.client_for(alias), "profile", None), "api_key", None)
    )
    if missing:
        variables = sorted(
            {
                config.models[alias].api_key_env or "NOVELTY_API_KEY"
                for alias in missing
            }
        )
        raise WorkflowConfigurationError(
            "真实工作流缺少模型凭据：" + ", ".join(variables)
        )

    from novelty_agent_framework.processing import DefaultPaperProcessor, MineruSettings

    processor = DefaultPaperProcessor(
        parser=str(processing.get("parser", "mineru")),
        ocr_client=(
            registry.client_for(processing["ocr_model"])
            if processing.get("ocr_model")
            else None
        ),
        llm_client=(
            registry.client_for(processing["llm_model"])
            if processing.get("llm_model")
            else None
        ),
        dpi=int(processing.get("dpi", 200)),
        min_chars_per_page=int(processing.get("quality_min_chars_per_page", 200)),
        mineru_settings=MineruSettings(
            python_path=processing.get("mineru_python"),
            env_name=processing.get("mineru_env", "mineru"),
            worker_path=processing.get("mineru_worker", "scripts/mineru_worker.py"),
            backend=processing.get("mineru_backend", "pipeline"),
            method=processing.get("mineru_method", "auto"),
            lang=processing.get("mineru_lang", "ch"),
            effort=processing.get("mineru_effort", "medium"),
            timeout_seconds=int(processing.get("mineru_timeout_seconds", 1800)),
            work_root=processing.get("mineru_work_root", "outputs/.mineru"),
            model_source=processing.get("mineru_model_source"),
        ),
    )

    def workflow_factory(output_root: Path) -> NoveltyWorkflow:
        run_config = config.model_copy(deep=True)
        run_config.project.runtime_debug.output_root = str(output_root)
        run_config.project.runtime_debug.archive_root = str(
            output_root / "runtime-archive"
        )
        return build_standard_full_workflow(run_config, output_root=output_root)

    return NoveltyWorkflowService(
        workflow_factory=workflow_factory,
        processor=processor,
        runs_root=settings.runs_root,
        max_upload_bytes=settings.max_upload_bytes,
    )


def build_demo_workflow_service(settings: NoveltyWebSettings) -> NoveltyWorkflowService:
    from novelty_agent_framework.processing import DefaultPaperProcessor

    return NoveltyWorkflowService(
        workflow_factory=lambda output_root: NoveltyWorkflow.default(
            output_root=output_root
        ),
        processor=DefaultPaperProcessor(parser="text_layer"),
        runs_root=settings.runs_root,
        max_upload_bytes=settings.max_upload_bytes,
    )
