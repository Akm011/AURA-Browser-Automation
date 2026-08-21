from typing import Any
from unittest.mock import AsyncMock

import pytest
from aura_models.config import AuraSettings
from aura_models.planning import ExecutionPlan, PlanStep
from aura_skills import ActionExecutor, BrowserSkill, SkillRegistry, SkillResult
from aura_skills.base import SkillContext


class SuccessfulSkill(BrowserSkill):
    name = "Successful"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        return SkillResult(success=True, message="completed", data={"value": kwargs["value"]})


class FailingSkill(BrowserSkill):
    name = "Failing"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        return SkillResult(success=False, message="expected failure")


class Response:
    def __init__(self, ok: bool, status: int) -> None:
        self.ok = ok
        self.status = status


class FakePage:
    def __init__(self, responses: list[Response | None] | None = None) -> None:
        self.responses = responses or []
        self.goto_calls: list[dict[str, Any]] = []

    async def goto(self, url: str, *, wait_until: str) -> Response | None:
        self.goto_calls.append({"url": url, "wait_until": wait_until})
        return self.responses.pop(0) if self.responses else Response(True, 200)

    async def title(self) -> str:
        return "AURA test page"


@pytest.mark.asyncio
async def test_executor_returns_success_for_empty_plan() -> None:
    plan = ExecutionPlan(request="nothing")
    result = await ActionExecutor().execute_plan(plan, FakePage())

    assert result.success is True
    assert result.step_results == []


@pytest.mark.asyncio
async def test_executor_runs_registered_skill_and_keeps_output() -> None:
    registry = SkillRegistry(skills=[])
    registry.register(SuccessfulSkill())
    plan = ExecutionPlan(
        request="run skill",
        steps=[PlanStep(skill="Successful", params={"value": "AURA"})],
    )

    result = await ActionExecutor(registry=registry).execute_plan(plan, FakePage())

    assert result.success is True
    assert result.step_results[0].data == {"value": "AURA"}


@pytest.mark.asyncio
async def test_executor_stops_at_first_skill_failure() -> None:
    registry = SkillRegistry(skills=[])
    registry.register(FailingSkill())
    registry.register(SuccessfulSkill())
    plan = ExecutionPlan(
        request="fail",
        steps=[
            PlanStep(skill="Failing"),
            PlanStep(skill="Successful", params={"value": "not run"}),
        ],
    )

    result = await ActionExecutor(registry=registry).execute_plan(plan, FakePage())

    assert result.success is False
    assert result.error == "expected failure"
    assert len(result.step_results) == 1


@pytest.mark.asyncio
async def test_executor_rejects_unknown_skill() -> None:
    plan = ExecutionPlan(request="unknown", steps=[PlanStep(skill="DoesNotExist")])

    result = await ActionExecutor(SkillRegistry(skills=[])).execute_plan(plan, FakePage())

    assert result.success is False
    assert result.error == "Unknown skill: DoesNotExist"


@pytest.mark.asyncio
async def test_navigation_retries_once_then_returns_page_title() -> None:
    page = FakePage([Response(False, 503), Response(True, 200)])
    plan = ExecutionPlan(
        request="open",
        steps=[PlanStep(skill="Navigate", params={"url": "https://example.com"})],
    )

    result = await ActionExecutor().execute_plan(plan, page)

    assert result.success is True
    assert len(page.goto_calls) == 2
    assert result.step_results[0].data == {"title": "AURA test page"}


@pytest.mark.asyncio
async def test_navigation_without_url_returns_a_clear_failure() -> None:
    plan = ExecutionPlan(request="open", steps=[PlanStep(skill="Navigate")])

    result = await ActionExecutor().execute_plan(plan, FakePage())

    assert result.success is False
    assert result.error == "Navigate step requires url param"


@pytest.mark.asyncio
async def test_executor_pauses_after_each_successful_step(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = SkillRegistry(skills=[])
    registry.register(SuccessfulSkill())
    sleep = AsyncMock()
    monkeypatch.setattr("aura_skills.executor.asyncio.sleep", sleep)
    plan = ExecutionPlan(
        request="pause",
        steps=[
            PlanStep(skill="Successful", params={"value": "first"}),
            PlanStep(skill="Successful", params={"value": "last"}),
        ],
    )
    settings = AuraSettings(_env_file=None, browser_step_delay_seconds=1.5)

    result = await ActionExecutor(registry=registry, settings=settings).execute_plan(
        plan, FakePage()
    )

    assert result.success is True
    assert sleep.await_count == 2
    sleep.assert_awaited_with(1.5)
