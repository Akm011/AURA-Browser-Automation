from aura_planner import IntentParser


def test_parser_extracts_url_and_removes_trailing_punctuation() -> None:
    intent = IntentParser().parse("Open https://example.com/docs, please.")

    assert intent.target_url == "https://example.com/docs"
    assert intent.actions == ["navigate"]


def test_parser_preserves_action_order_and_deduplicates_actions() -> None:
    intent = IntentParser().parse(
        "Open https://example.com, click Settings, search for reports, then wait 5s."
    )

    assert intent.actions == ["navigate", "click", "search", "wait"]
    assert intent.entities["click_target"] == "Settings"
    assert intent.entities["search_query"] == "reports"
    assert intent.entities["wait_seconds"] == "5.0"


def test_parser_understands_quoted_values_and_menu_paths() -> None:
    intent = IntentParser().parse(
        'Open https://example.com and select "India" and navigate to Reports > Monthly menu'
    )

    assert intent.entities["quoted_text"] == "India"
    assert intent.entities["menu_path"] == "Reports > Monthly"


def test_parser_defaults_to_navigation_for_plain_request() -> None:
    intent = IntentParser().parse("Show the company home page")

    assert intent.target_url is None
    assert intent.actions == ["navigate"]
    assert intent.goal == "Show the company home page"
