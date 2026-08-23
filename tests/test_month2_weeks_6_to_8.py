from aura_browser import DOMAnalyzer, NavigationGraphBuilder
from aura_execution.task_store import TaskStore
from aura_models.planning import ExecutionPlan, PlanStep
from aura_planner import PlanValidator
from aura_skills import default_registry


def test_month2_dom_navigation_tools_and_timeline() -> None:
    summary = {
        "url": "https://example.com",
        "links": [{"name": "Reports", "href": "https://example.com/reports"}],
    }
    assert NavigationGraphBuilder.build(summary)["edges"][0]["label"] == "Reports"
    assert DOMAnalyzer.locator_for({"role": "button", "name": "Save"}) == {
        "role": "button", "name": "Save"
    }
    assert default_registry().tool_definitions()[0]["inputSchema"]["type"] == "object"
    assert PlanValidator().validate(
        ExecutionPlan(request="open", steps=[PlanStep(skill="Navigate", params={"url": "https://example.com"})])
    )
    task = TaskStore().create("Open https://example.com", enqueue=False)
    assert task.timeline[0]["event"] == "created"
