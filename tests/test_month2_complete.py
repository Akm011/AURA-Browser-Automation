import json
from types import SimpleNamespace

from aura_models.config import AuraSettings
from aura_models.planning import ExecutionPlan, PlanExecutionResult, PlanStep
from aura_planner import ExecutionPlanner, IntentParser, LiteLLMRequestAnalyzer, PlanValidator
from aura_skills import default_registry


def test_month_two_has_twelve_reusable_skills_and_mcp_descriptions() -> None:
    registry = default_registry()

    assert len(registry.list_names()) >= 12
    assert {"DownloadFile", "ExtractText", "PressKey", "ScrollPage", "UploadFile"} <= set(
        registry.list_names()
    )
    assert len(registry.tool_definitions()) >= 12


def test_download_task_selects_the_download_skill() -> None:
    intent = IntentParser().parse("Open https://example.com and download latest report")
    plan = ExecutionPlanner().plan(intent)

    assert [step.skill for step in plan.steps] == ["Navigate", "DownloadFile"]


def test_login_and_upload_plans_require_human_approval() -> None:
    login_plan = ExecutionPlan(
        request="login",
        steps=[
            PlanStep(skill="FillInput", params={"selector": "input[type=password]"}),
            PlanStep(skill="ClickElement", params={"selector": "button[type=submit]"}),
        ],
    )
    upload_plan = ExecutionPlan(request="upload", steps=[PlanStep(skill="UploadFile")])

    assert PlanValidator().validate(login_plan).requires_approval is True
    assert PlanValidator().validate(upload_plan).requires_approval is True


def test_execution_validator_reports_a_failed_step() -> None:
    result = PlanExecutionResult(
        success=False,
        plan=ExecutionPlan(request="test"),
        step_results=[
            {"step_index": 0, "skill": "ClickElement", "success": False, "message": "missing"}
        ],
    )

    assert PlanValidator.validate_result(result) == {
        "valid": False,
        "completed_steps": 1,
        "failed_step": 0,
    }


def test_litellm_analyzer_uses_structured_output_adapter() -> None:
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=json.dumps(
                        {
                            "goal": "Open site",
                            "target_url": "https://example.com",
                            "actions": ["navigate"],
                            "entities": {},
                            "planner_steps": [
                                {
                                    "skill": "Navigate",
                                    "params": {"url": "https://example.com"},
                                    "description": "Open site",
                                }
                            ],
                            "credentials_provided": False,
                            "correction_suggestions": [],
                            "needs_clarification": False,
                            "clarification_reason": None,
                        }
                    )
                )
            )
        ]
    )
    calls: list[dict] = []

    def completion(**kwargs):
        calls.append(kwargs)
        return response

    analyzer = LiteLLMRequestAnalyzer(
        settings=AuraSettings(openai_api_key="key", litellm_model="openai/test"),
        completion=completion,
    )
    intent = analyzer.analyze("Open https://example.com")

    assert calls[0]["model"] == "openai/test"
    assert intent.proposed_steps[0]["skill"] == "Navigate"
