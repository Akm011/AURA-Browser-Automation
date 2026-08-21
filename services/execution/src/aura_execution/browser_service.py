from __future__ import annotations

import asyncio

from aura_browser import BrowserManager, configure_logging
from aura_models.config import AuraSettings, get_settings
from aura_models.planning import (
    ExecutionPlan,
    PlanExecutionResult,
)
from aura_planner import PlannerAgent
from aura_skills import ActionExecutor

from aura_execution.task_store import (
    TaskRecord,
    TaskStatus,
    TaskStore,
)


class BrowserExecutionService:
    """Orchestrates planning and browser execution."""

    def __init__(
        self,
        settings: AuraSettings | None = None,
        task_store: TaskStore | None = None,
        planner: PlannerAgent | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.task_store = task_store or TaskStore()
        self.planner = planner or PlannerAgent()

        self._worker_task: asyncio.Task | None = None

    def list_skills(self) -> list[str]:
        return (
            ActionExecutor()
            .registry
            .list_names()
            + [
                ActionExecutor.NAVIGATE_SKILL,
                "Wait",
            ]
        )

    def create_plan(
        self,
        request: str,
    ) -> ExecutionPlan:
        return self.planner.plan(request)

    async def execute_sync(
        self,
        request: str,
        *,
        headed: bool | None = None,
        plan_only: bool = False,
    ) -> ExecutionPlan | PlanExecutionResult:
        settings = self._runtime_settings(headed)
        configure_logging(settings)

        plan = self.create_plan(request)

        if plan_only:
            return plan

        task = self.task_store.create(
            request,
            headed=bool(headed),
            enqueue=False,
        )

        self.task_store.update(
            task.id,
            status=TaskStatus.RUNNING,
            plan=plan,
        )

        try:
            result = await self._run_plan(
                plan,
                settings,
                run_id=task.id,
            )

            status = (
                TaskStatus.COMPLETED
                if result.success
                else TaskStatus.FAILED
            )

            self.task_store.update(
                task.id,
                status=status,
                result=result,
                error=result.error,
            )

            return result

        except Exception as exc:
            self.task_store.update(
                task.id,
                status=TaskStatus.FAILED,
                error=str(exc),
            )
            raise

    async def enqueue(
        self,
        request: str,
        *,
        headed: bool = False,
    ) -> TaskRecord:
        task = self.task_store.create(
            request,
            headed=headed,
        )

        self._ensure_worker()

        return task

    def get_task(
        self,
        task_id: str,
    ) -> TaskRecord | None:
        return self.task_store.get(task_id)

    def list_tasks(
        self,
        limit: int = 50,
    ) -> list[TaskRecord]:
        return self.task_store.list_tasks(
            limit=limit
        )

    async def _run_plan(
        self,
        plan: ExecutionPlan,
        settings: AuraSettings,
        *,
        run_id: str | None = None,
    ) -> PlanExecutionResult:
        executor = ActionExecutor(
            settings=settings,
            run_id=run_id,
        )

        async with BrowserManager(settings).session() as browser:
            page = await browser.new_page()

            return await executor.execute_plan(
                plan,
                page,
            )

    def _runtime_settings(
        self,
        headed: bool | None,
    ) -> AuraSettings:
        settings = self.settings.model_copy(
            deep=True
        )

        if headed is not None:
            settings.browser_headless = not headed

        settings.ensure_directories()

        return settings

    def _ensure_worker(self) -> None:
        if (
            self._worker_task is None
            or self._worker_task.done()
        ):
            self._worker_task = asyncio.create_task(
                self._worker_loop()
            )

    async def _worker_loop(self) -> None:
        while True:
            task_id = self.task_store.pop_pending()

            if task_id is None:
                await asyncio.sleep(0.2)

                if self.task_store.pending_count() == 0:
                    break

                continue

            await self._process_task(task_id)

    async def _process_task(
        self,
        task_id: str,
    ) -> None:
        task = self.task_store.get(task_id)

        if task is None:
            return

        self.task_store.update(
            task_id,
            status=TaskStatus.RUNNING,
        )

        settings = self._runtime_settings(
            task.headed
        )

        configure_logging(settings)

        try:
            plan = self.create_plan(
                task.request
            )

            result = await self._run_plan(
                plan,
                settings,
                run_id=task.id,
            )

            status = (
                TaskStatus.COMPLETED
                if result.success
                else TaskStatus.FAILED
            )

            self.task_store.update(
                task_id,
                status=status,
                plan=plan,
                result=result,
                error=result.error,
            )

        except Exception as exc:
            self.task_store.update(
                task_id,
                status=TaskStatus.FAILED,
                error=str(exc),
            )

    async def shutdown(self) -> None:
        if self._worker_task is not None:
            await self._worker_task