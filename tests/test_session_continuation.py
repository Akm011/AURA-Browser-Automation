from aura_execution.browser_service import BrowserExecutionService
from aura_execution.task_store import TaskStore
from aura_models.planning import ExecutionPlan, PlanStep


def test_follow_up_plan_resumes_the_last_session_url() -> None:
    plan = ExecutionPlan(request="Click Reports", steps=[PlanStep(skill="ClickElement")])

    resumed = BrowserExecutionService._resume_plan(plan, "https://example.com/dashboard")

    assert [step.skill for step in resumed.steps] == ["Navigate", "ClickElement"]
    assert resumed.steps[0].params == {"url": "https://example.com/dashboard"}


def test_explicit_url_is_not_replaced_by_session_memory() -> None:
    plan = ExecutionPlan(
        request="Open another page",
        steps=[PlanStep(skill="Navigate", params={"url": "https://example.com/other"})],
    )

    resumed = BrowserExecutionService._resume_plan(plan, "https://example.com/dashboard")

    assert resumed is plan


def test_task_id_becomes_the_default_session_id() -> None:
    store = TaskStore()
    service = BrowserExecutionService(task_store=store)
    task = store.create("Open https://example.com", enqueue=False)

    assigned = service._ensure_session_id(task)

    assert assigned.session_id == assigned.id
