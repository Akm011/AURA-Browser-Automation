from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from aura_models.planning import ExecutionPlan, PlanExecutionResult


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    request: str
    status: TaskStatus = TaskStatus.PENDING
    headed: bool = False
    plan: ExecutionPlan | None = None
    result: PlanExecutionResult | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self, **updates: Any) -> "TaskRecord":
        data = self.model_dump()
        data.update(updates)
        data["updated_at"] = datetime.now(timezone.utc)
        return TaskRecord.model_validate(data)


class TaskStore:
    """In-memory task queue and result store (Stack & Queue pattern for Week 3)."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskRecord] = {}
        self._pending_queue: list[str] = []

    def create( self, request: str, *, headed: bool = False, enqueue: bool = True, ) -> TaskRecord:
        task = TaskRecord( request=request, headed=headed, )
        self._tasks[task.id] = task
        if enqueue:
            self._pending_queue.append(task.id)
        return task

    def get(self, task_id: str) -> TaskRecord | None:
        return self._tasks.get(task_id)

    def update(self, task_id: str, **updates: Any) -> TaskRecord | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        updated = task.touch(**updates)
        self._tasks[task_id] = updated
        return updated

    def list_tasks(self, limit: int = 50) -> list[TaskRecord]:
        tasks = sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]

    def pop_pending(self) -> str | None:
        if not self._pending_queue:
            return None
        return self._pending_queue.pop(0)

    def pending_count(self) -> int:
        return len(self._pending_queue)
