"""论文查新任务 API。"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from novelty_agent_framework.schemas import PaperInput
from novelty_agent_framework.services.jobs import RunSnapshot

from ..services import NoveltyWorkflowService, get_novelty_workflow_service

router = APIRouter(prefix="/runs", tags=["novelty-runs"])


@router.post("", response_model=RunSnapshot, status_code=status.HTTP_202_ACCEPTED)
async def create_run(
    paper: PaperInput,
    background_tasks: BackgroundTasks,
    service: NoveltyWorkflowService = Depends(get_novelty_workflow_service),
) -> RunSnapshot:
    snapshot = service.create_run()
    background_tasks.add_task(service.execute, snapshot.task_id, paper)
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
