from typing import Any

from aura_skills import BrowserSkill, SkillContext, SkillRegistry, SkillResult, default_registry


def test_default_registry_exposes_all_month_one_skills() -> None:
    registry = default_registry()

    assert registry.list_names() == [
        "ClickElement",
        "FillInput",
        "FindLoginForm",
        "FindSearchBar",
        "NavigateMenu",
        "SelectDropdown",
        "Wait",
    ]
    assert registry.get("Wait") is not None
    assert registry.get("Unknown") is None


class ExampleSkill(BrowserSkill):
    name = "Example"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        return SkillResult(success=True, message="done")


def test_registry_can_register_a_custom_skill() -> None:
    registry = SkillRegistry(skills=[])
    registry.register(ExampleSkill())

    assert registry.get("Example").name == "Example"  # type: ignore[union-attr]
