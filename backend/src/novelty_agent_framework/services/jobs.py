"""Web V0 使用的进程内任务状态存储。"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from threading import RLock
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RunSnapshot(BaseModel):
    """前端轮询任务状态时使用的统一响应。"""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    result: dict[str, Any] | None = None
    error: str | None = None


class InMemoryRunStore:
    """开发阶段任务存储；生产部署应替换为 Redis 或数据库。"""

    def __init__(self) -> None:
        self._runs: dict[str, RunSnapshot] = {}
        self._lock = RLock()

    def create(self) -> RunSnapshot:
        now = datetime.now(UTC)
        snapshot = RunSnapshot(
            task_id=uuid4().hex,
            status=RunStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._runs[snapshot.task_id] = snapshot
        return snapshot.model_copy(deep=True)

    def mark_running(self, task_id: str) -> RunSnapshot:
        return self._update(task_id, status=RunStatus.RUNNING, result=None, error=None)

    def mark_succeeded(self, task_id: str, result: dict[str, Any]) -> RunSnapshot:
        return self._update(
            task_id,
            status=RunStatus.SUCCEEDED,
            result=result,
            error=None,
        )

    def mark_failed(self, task_id: str, error: str) -> RunSnapshot:
        return self._update(
            task_id,
            status=RunStatus.FAILED,
            result=None,
            error=error,
        )

    def get(self, task_id: str) -> RunSnapshot | None:
        with self._lock:
            snapshot = self._runs.get(task_id)
            return snapshot.model_copy(deep=True) if snapshot else None

    def _update(self, task_id: str, **changes: Any) -> RunSnapshot:
        with self._lock:
            current = self._runs.get(task_id)
            if current is None:
                raise KeyError(task_id)
            updated = current.model_copy(
                update={**changes, "updated_at": datetime.now(UTC)},
                deep=True,
            )
            self._runs[task_id] = updated
            return updated.model_copy(deep=True)
