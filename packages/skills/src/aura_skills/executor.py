from __future__ import annotations

import asyncio
import time
from typing import Any

from aura_browser import DOMAnalyzer, NavigationGraphBuilder, get_logger
from aura_models.config import AuraSettings
from aura_models.planning import (
    ExecutionPlan,
    PlanExecutionResult,
    PlanStep,
    StepExecutionResult,
)
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from aura_skills.base import SkillContext
from aura_skills.registry import SkillRegistry, default_registry

logger = get_logger(__name__)


class ActionExecutor:
    """Runs an execution plan against a live Playwright page."""

    NAVIGATE_SKILL = "Navigate"

    def __init__(
        self,
        registry: SkillRegistry | None = None,
        settings: AuraSettings | None = None,
        run_id: str | None = None,
    ) -> None:
        self.registry = registry or default_registry()
        self.settings = settings or AuraSettings()
        self.run_id = run_id

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        page: Page,
    ) -> PlanExecutionResult:
        step_results: list[StepExecutionResult] = []

        for index, step in enumerate(plan.steps):
            result = await self._execute_step(
                index,
                step,
                page,
            )

            step_results.append(result)

            if not result.success:
                return PlanExecutionResult(
                    success=False,
                    plan=plan,
                    step_results=step_results,
                    error=result.message,
                )

            await self._pause_after_step(index, step)

        return PlanExecutionResult(
            success=True,
            plan=plan,
            step_results=step_results,
        )

    async def _pause_after_step(self, index: int, step: PlanStep) -> None:
        """Pause after each successful step when interactive debugging is enabled."""
        delay_seconds = self.settings.browser_step_delay_seconds
        if delay_seconds <= 0:
            return

        logger.info(
            "step.pause",
            run_id=self.run_id,
            step_index=index,
            skill=step.skill,
            delay_seconds=delay_seconds,
        )
        await asyncio.sleep(delay_seconds)

    async def _execute_step(
        self,
        index: int,
        step: PlanStep,
        page: Page,
    ) -> StepExecutionResult:
        started = time.perf_counter()

        logger.info(
            "step.started",
            run_id=self.run_id,
            step_index=index,
            skill=step.skill,
        )

        try:
            if step.skill == self.NAVIGATE_SKILL:
                result = await self._navigate(
                    index,
                    step,
                    page,
                )
            else:
                skill = self.registry.get(step.skill)

                if skill is None:
                    result = StepExecutionResult(
                        step_index=index,
                        skill=step.skill,
                        success=False,
                        message=f"Unknown skill: {step.skill}",
                    )
                else:
                    context = SkillContext(
                        page=page,
                        settings=self.settings,
                    )

                    outcome = await skill.execute(
                        context,
                        **step.params,
                    )

                    result = StepExecutionResult(
                        step_index=index,
                        skill=step.skill,
                        success=outcome.success,
                        message=outcome.message,
                        data=outcome.data,
                    )

            duration_ms = (
                time.perf_counter() - started
            ) * 1000

            logger.info(
                "step.completed",
                run_id=self.run_id,
                step_index=index,
                skill=step.skill,
                success=result.success,
                duration_ms=round(duration_ms, 2),
                message=result.message,
            )

            return result

        except Exception:
            duration_ms = (
                time.perf_counter() - started
            ) * 1000

            logger.exception(
                "step.failed",
                run_id=self.run_id,
                step_index=index,
                skill=step.skill,
                duration_ms=round(duration_ms, 2),
            )

            raise

    async def _navigate(
        self,
        index: int,
        step: PlanStep,
        page: Page,
    ) -> StepExecutionResult:
        url = step.params.get("url")

        if not url:
            return StepExecutionResult(
                step_index=index,
                skill=step.skill,
                success=False,
                message="Navigate step requires url param",
            )

        # ponytail: retry only navigation; retrying arbitrary browser
        # actions can duplicate side effects.
        for attempt in range(2):
            try:
                response = await page.goto(
                    str(url),
                    wait_until="domcontentloaded",
                )

                if response is None or not response.ok:
                    status: Any = (
                        response.status
                        if response
                        else "no_response"
                    )

                    if attempt == 0:
                        logger.warning(
                            "navigate.retry",
                            run_id=self.run_id,
                            step_index=index,
                            url=str(url),
                            status=status,
                        )
                        continue

                    return StepExecutionResult(
                        step_index=index,
                        skill=step.skill,
                        success=False,
                        message=(
                            "Navigation failed "
                            f"with status: {status}"
                        ),
                    )

                title = await page.title()
                summary = (
                    await DOMAnalyzer().summarize(page)
                    if hasattr(page, "evaluate")
                    else None
                )

                return StepExecutionResult(
                    step_index=index,
                    skill=step.skill,
                    success=True,
                    message=f"Navigated to {url}",
                    data={
                        "title": title,
                        **({"page_summary": summary,
                            "navigation_graph": NavigationGraphBuilder.build(summary)}
                           if summary else {}),
                    },
                )

            except PlaywrightTimeoutError as exc:
                if attempt == 0:
                    logger.warning(
                        "navigate.retry",
                        run_id=self.run_id,
                        step_index=index,
                        url=str(url),
                        reason="timeout",
                    )
                    continue

                return StepExecutionResult(
                    step_index=index,
                    skill=step.skill,
                    success=False,
                    message=f"Navigation timeout: {exc}",
                )

        raise AssertionError("unreachable")
