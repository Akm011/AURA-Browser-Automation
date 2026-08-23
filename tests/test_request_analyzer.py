import json
from types import SimpleNamespace

from aura_models.config import AuraSettings
from aura_planner import ExecutionPlanner, OpenAIRequestAnalyzer


class FakeResponses:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


def test_analyzer_uses_terra_and_passes_credentials_to_planner_format() -> None:
    responses = FakeResponses(
        '''{"goal":"Log in and download the report","target_url":"https://example.com/login",'''
        '''"actions":["navigate","login","download"],"entities":{"username":"student",'''
        '''"password":"Password123"},"planner_steps":[{"skill":"Navigate",'''
        '''"params":{"url":"https://example.com/login"},"description":"Open site"}],'''
        '''"credentials_provided":true,"correction_suggestions":['''
        '''"Corrected 'downlod' to 'download'"],"needs_clarification":false,'''
        '''"clarification_reason":null}'''
    )
    client = SimpleNamespace(responses=responses)
    analyzer = OpenAIRequestAnalyzer(
        settings=AuraSettings(openai_api_key="test-key"),
        client=client,
    )

    intent = analyzer.analyze(
        "Log in to https://example.com/login using student / Password123 and downlod report"
    )

    assert responses.calls[0]["model"] == "gpt-5.6-terra"
    assert responses.calls[0]["reasoning"] == {"effort": "medium"}
    assert intent.credentials_provided is True
    assert intent.entities["username"] == "student"
    assert intent.entities["password"] == "Password123"
    assert intent.correction_suggestions == ["Corrected 'downlod' to 'download'"]


def test_analyzer_requires_credentials_for_login() -> None:
    responses = FakeResponses(
        '''{"goal":"Log in","target_url":"https://example.com/login","actions":["navigate","login"],'''
        '''"entities":{},"planner_steps":[],"credentials_provided":false,'''
        '''"correction_suggestions":[],"needs_clarification":true,"clarification_reason":null}'''
    )
    analyzer = OpenAIRequestAnalyzer(
        settings=AuraSettings(openai_api_key="test-key"),
        client=SimpleNamespace(responses=responses),
    )

    intent = analyzer.analyze("Open https://example.com/login and login")

    assert intent.credentials_provided is False
    assert intent.needs_clarification is True
    assert intent.clarification_reason == "Username and password are required to log in."


def test_analyzer_preserves_explicit_sign_in_click_and_normalizes_markdown_url() -> None:
    responses = FakeResponses(
        json.dumps(
            {
                "goal": "Sign in",
                "target_url": "[https://example.com](https://example.com)",
                "actions": ["navigate", "click", "login"],
                "entities": {
                    "username": "person@example.com",
                    "password": "not-a-real-password",
                    "click_target": "Sign In",
                },
                "planner_steps": [
                    {"skill": "Navigate", "params": {"url": "https://example.com"}},
                    {"skill": "ClickElement", "params": {"text": "Sign In"}},
                    {"skill": "FindLoginForm", "params": {}},
                    {
                        "skill": "FillInput",
                        "params": {
                            "selector": "input[type=email]",
                            "value": "person@example.com",
                        },
                    },
                    {
                        "skill": "FillInput",
                        "params": {
                            "selector": "input[type=password]",
                            "value": "not-a-real-password",
                        },
                    },
                    {
                        "skill": "ClickElement",
                        "params": {"selector": "button[type=submit]"},
                    },
                ],
                "credentials_provided": True,
                "correction_suggestions": [],
                "needs_clarification": False,
                "clarification_reason": None,
            }
        )
    )
    analyzer = OpenAIRequestAnalyzer(
        settings=AuraSettings(openai_api_key="test-key"),
        client=SimpleNamespace(responses=responses),
    )

    intent = analyzer.analyze(
        "Navigate to [https://example.com](https://example.com) and click Sign In"
    )

    assert intent.target_url == "https://example.com"
    assert intent.actions == ["navigate", "click", "login"]
    assert intent.entities["click_target"] == "Sign In"
    assert [step.skill for step in ExecutionPlanner().plan(intent).steps] == [
        "Navigate",
        "ClickElement",
        "FindLoginForm",
        "FillInput",
        "FillInput",
        "ClickElement",
    ]
