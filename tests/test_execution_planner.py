from aura_planner import ExecutionPlanner, IntentParser, PlannerAgent


def test_url_only_request_produces_navigation_step() -> None:
    plan = PlannerAgent().plan("Open https://example.com")

    assert [step.skill for step in plan.steps] == ["Navigate"]
    assert plan.steps[0].params == {"url": "https://example.com"}


def test_search_request_produces_find_fill_and_submit_steps() -> None:
    intent = IntentParser().parse("Open https://example.com and search for quarterly reports")
    plan = ExecutionPlanner().plan(intent)

    assert [step.skill for step in plan.steps] == [
        "Navigate",
        "FindSearchBar",
        "FillInput",
        "ClickElement",
    ]
    assert plan.steps[2].params["value"] == "quarterly reports"


def test_login_request_builds_complete_login_flow() -> None:
    intent = IntentParser().parse("Open https://example.com/login and login")
    plan = ExecutionPlanner().plan(intent)

    assert [step.skill for step in plan.steps] == [
        "Navigate",
        "FindLoginForm",
        "FillInput",
        "FillInput",
        "ClickElement",
    ]
    assert plan.steps[2].params["selector"] == "input[type='email'], input[type='text']"
    assert plan.steps[3].params["selector"] == "input[type='password']"


def test_menu_and_select_steps_use_parsed_values() -> None:
    intent = IntentParser().parse(
        'Open https://example.com and select "India" and navigate to Reports > Monthly menu'
    )
    plan = ExecutionPlanner().plan(intent)

    select_step = next(step for step in plan.steps if step.skill == "SelectDropdown")
    menu_step = next(step for step in plan.steps if step.skill == "NavigateMenu")
    assert select_step.params == {"value": "India"}
    assert menu_step.params == {"path": ["Reports", "Monthly"]}
