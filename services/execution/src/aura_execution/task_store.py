from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from aura_models.planning import (
    ExecutionPlan,
    PlanExecutionResult,
)
from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskRecord(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    request: str
    headed: bool = False
    session_id: str | None = None
    step_delay_seconds: float | None = None

    status: TaskStatus = TaskStatus.PENDING

    plan: ExecutionPlan | None = None
    result: PlanExecutionResult | None = None
    error: str | None = None
    timeline: list[dict[str, str]] = Field(default_factory=list)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    def touch(
        self,
        **updates: Any,
    ) -> TaskRecord:
        data = self.model_dump()
        data.update(updates)
        data["updated_at"] = datetime.now(UTC)

        return TaskRecord.model_validate(data)


class TaskStore:
    """In-memory task store and execution queue."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskRecord] = {}
        self._pending_queue: list[str] = []

    def create(
        self,
        request: str,
        *,
        headed: bool = False,
        session_id: str | None = None,
        step_delay_seconds: float | None = None,
        enqueue: bool = True,
    ) -> TaskRecord:
        task = TaskRecord(
            request=request,
            headed=headed,
            session_id=session_id,
            step_delay_seconds=step_delay_seconds,
        )

        self._tasks[task.id] = task
        task = self.add_event(task.id, "created", "Task created")

        if enqueue:
            self._pending_queue.append(task.id)

        return task

    def add_event(self, task_id: str, event: str, message: str) -> TaskRecord:
        task = self._tasks[task_id]
        timeline = [
            *task.timeline,
            {"at": datetime.now(UTC).isoformat(), "event": event, "message": message},
        ]
        return self.update(task_id, timeline=timeline)

    def get(
        self,
        task_id: str,
    ) -> TaskRecord | None:
        return self._tasks.get(task_id)

    def update(
        self,
        task_id: str,
        **updates: Any,
    ) -> TaskRecord:
        task = self._tasks[task_id]

        updated = task.touch(**updates)

        self._tasks[task_id] = updated

        return updated

    def list_tasks(
        self,
        limit: int = 50,
    ) -> list[TaskRecord]:
        tasks = list(self._tasks.values())

        tasks.sort(
            key=lambda task: task.created_at,
            reverse=True,
        )

        return tasks[:limit]

    def pop_pending(self) -> str | None:
        if not self._pending_queue:
            return None

        return self._pending_queue.pop(0)

    def pending_count(self) -> int:
        return len(self._pending_queue)
