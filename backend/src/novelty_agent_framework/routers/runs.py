"""论文查新任务 API。"""

from typing import Literal

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from novelty_agent_framework.schemas import PaperInput
from novelty_agent_framework.services.jobs import RunSnapshot

from ..services import NoveltyWorkflowService, UploadValidationError

router = APIRouter(prefix="/runs", tags=["novelty-runs"])


def get_novelty_workflow_service(request: Request) -> NoveltyWorkflowService:
    service = getattr(request.app.state, "workflow_service", None)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "workflow_unavailable",
                "message": "真实查新工作流尚未配置完成。",
            },
        )
    return service


@router.post("", response_model=RunSnapshot, status_code=status.HTTP_202_ACCEPTED)
async def create_run(
    paper: PaperInput,
    background_tasks: BackgroundTasks,
    service: NoveltyWorkflowService = Depends(get_novelty_workflow_service),
) -> RunSnapshot:
    snapshot = service.create_run()
    background_tasks.add_task(service.execute, snapshot.task_id, paper)
    return snapshot


@router.post(
    "/files", response_model=RunSnapshot, status_code=status.HTTP_202_ACCEPTED
)
async def create_file_run(
    background_tasks: BackgroundTasks,
    paper: UploadFile = File(...),
    references: list[UploadFile] | None = File(default=None),
    service: NoveltyWorkflowService = Depends(get_novelty_workflow_service),
) -> RunSnapshot:
    if references:
        for reference in references:
            await reference.close()
        await paper.close()
        raise HTTPException(
            status_code=422,
            detail={
                "code": "references_not_supported",
                "message": "参考文献上传尚未开放。",
            },
        )
    try:
        snapshot, path = await service.create_file_run(paper)
    except UploadValidationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc
    background_tasks.add_task(service.execute_file, snapshot.task_id, path)
    return snapshot


@router.get("/{task_id}", response_model=RunSnapshot)
async def get_run(
    task_id: str,
    service: NoveltyWorkflowService = Depends(get_novelty_workflow_service),
) -> RunSnapshot:
    snapshot = service.get_run(task_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="查新任务不存在")
    return snapshot


@router.get("/{task_id}/report", response_class=FileResponse)
async def get_report(
    task_id: str,
    disposition: Literal["inline", "attachment"] = Query(default="inline"),
    service: NoveltyWorkflowService = Depends(get_novelty_workflow_service),
) -> FileResponse:
    resource = service.get_report(task_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="查新报告不存在")
    path, filename = resource
    return FileResponse(
        path,
        media_type="text/markdown",
        filename=filename,
        content_disposition_type=disposition,
    )
