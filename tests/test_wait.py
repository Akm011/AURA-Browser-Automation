from aura_planner import ExecutionPlanner, IntentParser, PlannerAgent


def test_intent_parser_extracts_wait_and_click_target() -> None:
    request = (
        "Open https://www.geeksforgeeks.org/ and click devops and wait for 10 second"
    )
    intent = IntentParser().parse(request)

    assert intent.target_url == "https://www.geeksforgeeks.org/"
    assert intent.entities["click_target"] == "devops"
    assert intent.entities["wait_seconds"] == "10.0"
    assert intent.actions.index("click") < intent.actions.index("wait")


def test_execution_planner_adds_wait_after_click() -> None:
    request = (
        "Open https://www.geeksforgeeks.org/ and click devops and wait for 10 second"
    )
    plan = PlannerAgent().plan(request)

    assert [step.skill for step in plan.steps] == ["Navigate", "ClickElement", "Wait"]
    assert plan.steps[1].params["text"] == "devops"
    assert plan.steps[2].params["seconds"] == 10.0


def test_wait_supports_minutes() -> None:
    intent = IntentParser().parse("Open https://example.com and wait for 2 minutes")
    assert intent.entities["wait_seconds"] == "120.0"

    plan = ExecutionPlanner().plan(intent)
    assert plan.steps[-1].skill == "Wait"
    assert plan.steps[-1].params["seconds"] == 120.0
