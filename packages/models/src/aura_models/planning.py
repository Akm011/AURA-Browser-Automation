from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParsedIntent(BaseModel):
    """Structured understanding of a natural-language browser task."""

    raw_request: str
    target_url: str | None = None
    goal: str = ""
    actions: list[str] = Field(default_factory=list)
    entities: dict[str, str] = Field(default_factory=dict)
    proposed_steps: list[dict[str, Any]] = Field(default_factory=list)
    credentials_provided: bool = False
    correction_suggestions: list[str] = Field(default_factory=list)
    needs_clarification: bool = False
    clarification_reason: str | None = None


class PlanStep(BaseModel):
    """A single step in an execution plan."""

    skill: str
    params: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class ExecutionPlan(BaseModel):
    """Ordered browser skill steps produced by the execution planner."""

    request: str
    steps: list[PlanStep] = Field(default_factory=list)


class StepExecutionResult(BaseModel):
    step_index: int
    skill: str
    success: bool
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class PlanExecutionResult(BaseModel):
    success: bool
    plan: ExecutionPlan
    step_results: list[StepExecutionResult] = Field(default_factory=list)
    error: str | None = None
    screenshot_path: str | None = None
