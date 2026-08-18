from __future__ import annotations

from typing import Any

from playwright.async_api import Page

from aura_models.config import AuraSettings
from aura_models.planning import ExecutionPlan, PlanExecutionResult, PlanStep, StepExecutionResult
from aura_skills.base import SkillContext
from aura_skills.registry import SkillRegistry, default_registry


class ActionExecutor:
    """Runs an execution plan against a live Playwright page."""

    NAVIGATE_SKILL = "Navigate"

    def __init__(
        self,
        registry: SkillRegistry | None = None,
        settings: AuraSettings | None = None,
    ) -> None:
        self.registry = registry or default_registry()
        self.settings = settings or AuraSettings()

    async def execute_plan(self, plan: ExecutionPlan, page: Page) -> PlanExecutionResult:
        step_results: list[StepExecutionResult] = []

        for index, step in enumerate(plan.steps):
            result = await self._execute_step(index, step, page)
            step_results.append(result)
            if not result.success:
                return PlanExecutionResult(
                    success=False,
                    plan=plan,
                    step_results=step_results,
                    error=result.message,
                )

        return PlanExecutionResult(success=True, plan=plan, step_results=step_results)

    async def _execute_step(
        self,
        index: int,
        step: PlanStep,
        page: Page,
    ) -> StepExecutionResult:
        if step.skill == self.NAVIGATE_SKILL:
            return await self._navigate(index, step, page)

        skill = self.registry.get(step.skill)
        if skill is None:
            return StepExecutionResult(
                step_index=index,
                skill=step.skill,
                success=False,
                message=f"Unknown skill: {step.skill}",
            )

        context = SkillContext(page=page, settings=self.settings)
        outcome = await skill.execute(context, **step.params)
        return StepExecutionResult(
            step_index=index,
            skill=step.skill,
            success=outcome.success,
            message=outcome.message,
            data=outcome.data,
        )

    async def _navigate(self, index: int, step: PlanStep, page: Page) -> StepExecutionResult:
        url = step.params.get("url")
        if not url:
            return StepExecutionResult(
                step_index=index,
                skill=step.skill,
                success=False,
                message="Navigate step requires url param",
            )

        response = await page.goto(str(url), wait_until="domcontentloaded")
        if response is None or not response.ok:
            status: Any = response.status if response else "no_response"
            return StepExecutionResult(
                step_index=index,
                skill=step.skill,
                success=False,
                message=f"Navigation failed with status: {status}",
            )

        title = await page.title()
        return StepExecutionResult(
            step_index=index,
            skill=step.skill,
            success=True,
            message=f"Navigated to {url}",
            data={"title": title},
        )
