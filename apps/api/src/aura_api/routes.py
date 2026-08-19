from __future__ import annotations

from fastapi import APIRouter, HTTPException

from aura_api.schemas import (
    ExecuteRequest,
    HealthResponse,
    PlanRequest,
    SkillsResponse,
    TaskCreateRequest,
    TaskResponse,
)
from aura_api.dependencies import get_execution_service, get_settings
from aura_execution.task_store import TaskRecord

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
    )


@router.get("/skills", response_model=SkillsResponse)
async def list_skills() -> SkillsResponse:
    service = get_execution_service()
    return SkillsResponse(skills=service.list_skills())


@router.post("/plan")
async def create_plan(body: PlanRequest):
    service = get_execution_service()
    plan = service.create_plan(body.request)
    return plan.model_dump(mode="json")


@router.post("/execute")
async def execute_task(body: ExecuteRequest):
    service = get_execution_service()
    outcome = await service.execute_sync(
        body.request,
        headed=body.headed,
        plan_only=body.plan_only,
    )
    return outcome.model_dump(mode="json")


@router.post("/tasks", response_model=TaskResponse, status_code=202)
async def create_task(body: TaskCreateRequest) -> TaskResponse:
    service = get_execution_service()
    task = await service.enqueue(body.request, headed=body.headed)
    return _to_task_response(task)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(limit: int = 20) -> list[TaskResponse]:
    service = get_execution_service()
    return [_to_task_response(task) for task in service.list_tasks(limit=limit)]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    service = get_execution_service()
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_task_response(task)


def _to_task_response(task: TaskRecord) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        request=task.request,
        status=task.status.value,
        headed=task.headed,
        plan=task.plan,
        result=task.result,
        error=task.error,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )
