from __future__ import annotations

from pydantic import BaseModel, Field

from aura_models.planning import ExecutionPlan, PlanExecutionResult


class PlanRequest(BaseModel):
    request: str = Field(..., min_length=3, examples=["Open https://example.com and click More information"])


class ExecuteRequest(BaseModel):
    request: str = Field(..., min_length=3)
    headed: bool = False
    step_delay_seconds: float | None = Field(default=None, ge=0)
    plan_only: bool = False


class TaskCreateRequest(BaseModel):
    request: str = Field(..., min_length=3)
    headed: bool = False
    step_delay_seconds: float = Field(default=0, ge=0)


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class SkillsResponse(BaseModel):
    skills: list[str]


class TaskResponse(BaseModel):
    id: str
    request: str
    status: str
    headed: bool
    step_delay_seconds: float
    plan: ExecutionPlan | None = None
    result: PlanExecutionResult | None = None
    error: str | None = None
    created_at: str
    updated_at: str
