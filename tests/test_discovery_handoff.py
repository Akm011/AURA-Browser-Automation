from aura_browser.sessions import SessionManager
from aura_execution.browser_service import BrowserExecutionService
from aura_models.config import AuraSettings
from aura_models.planning import ExecutionPlan, PlanStep
from aura_planner import PlannerAgent


def test_discovery_is_persisted_in_session_memory(tmp_path) -> None:
    sessions = SessionManager(tmp_path)
    sessions.record_discovery("demo", {"url": "https://example.com", "elements": []})

    assert sessions.load_memory("demo")["discovery"]["url"] == "https://example.com"


def test_discovery_adds_url_and_exact_click_hint() -> None:
    plan = ExecutionPlan(request="Click reports", steps=[PlanStep(skill="ClickElement", params={"text": "reports"})])

    hinted = PlannerAgent._apply_discovery_hints(plan, {
        "url": "https://example.com/dashboard",
        "elements": [{"name": "Reports & analytics", "id": "reports-link"}],
    })

    assert [step.skill for step in hinted.steps] == ["Navigate", "ClickElement"]
    assert hinted.steps[1].params == {"selector": "#reports-link"}


def test_execution_service_uses_saved_discovery_for_its_plan(tmp_path) -> None:
    settings = AuraSettings(_env_file=None, sessions_dir=tmp_path, openai_api_key=None)
    SessionManager(tmp_path).record_discovery("demo", {
        "url": "https://example.com/dashboard",
        "elements": [{"name": "Reports", "id": "reports"}],
    })
    service = BrowserExecutionService(settings=settings, planner=PlannerAgent(settings=settings))

    plan = service.create_plan("Click reports", session_id="demo")

    assert plan.steps[0].params == {"url": "https://example.com/dashboard"}
    assert plan.steps[1].params == {"selector": "#reports"}
