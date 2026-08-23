from __future__ import annotations

from pydantic import BaseModel, Field

from aura_models.planning import ExecutionPlan, PlanExecutionResult


class PlanRequest(BaseModel):
    request: str = Field(..., min_length=3, examples=["Open https://example.com and click More information"])


class ExecuteRequest(BaseModel):
    request: str = Field(..., min_length=3)
    headed: bool = False
    session_id: str | None = Field(default=None, min_length=1, max_length=100)
    step_delay_seconds: float | None = Field(default=None, ge=0)
    plan_only: bool = False


class TaskCreateRequest(BaseModel):
    request: str = Field(..., min_length=3)
    headed: bool = False
    session_id: str | None = Field(default=None, min_length=1, max_length=100)
    step_delay_seconds: float | None = Field(default=None, ge=0)


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class SkillsResponse(BaseModel):
    skills: list[str]
    tools: list[dict] = Field(default_factory=list)


class TaskResponse(BaseModel):
    id: str
    request: str
    status: str
    headed: bool
    session_id: str | None
    step_delay_seconds: float | None
    plan: ExecutionPlan | None = None
    result: PlanExecutionResult | None = None
    error: str | None = None
    timeline: list[dict[str, str]] = Field(default_factory=list)
    created_at: str
    updated_at: str
