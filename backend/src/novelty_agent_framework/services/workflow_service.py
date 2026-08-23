"""论文查新任务的应用服务。"""

from __future__ import annotations

from functools import lru_cache

from novelty_agent_framework.schemas import PaperInput
from novelty_agent_framework.services.jobs import InMemoryRunStore, RunSnapshot
from novelty_agent_framework.workflows import NoveltyWorkflow


class NoveltyWorkflowService:
    def __init__(
        self,
        workflow: NoveltyWorkflow | None = None,
        store: InMemoryRunStore | None = None,
    ) -> None:
        self.workflow = workflow or NoveltyWorkflow.default()
        self.store = store or InMemoryRunStore()

    def create_run(self) -> RunSnapshot:
        return self.store.create()

    async def execute(self, task_id: str, paper: PaperInput) -> None:
        self.store.mark_running(task_id)
        try:
            result = await self.workflow.arun(paper)
            self.store.mark_succeeded(task_id, result.model_dump(mode="json"))
        except Exception as exc:
            self.store.mark_failed(task_id, str(exc))

    def get_run(self, task_id: str) -> RunSnapshot | None:
        return self.store.get(task_id)


@lru_cache(maxsize=1)
def get_novelty_workflow_service() -> NoveltyWorkflowService:
    return NoveltyWorkflowService()
