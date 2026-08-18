from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult
from aura_skills.helpers import resolve_input


class SelectDropdown(BrowserSkill):
    name = "SelectDropdown"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        page = context.playwright_page
        value = kwargs.get("value")
        if value is None:
            return SkillResult(success=False, message="Missing required param: value")

        locator = await resolve_input(
            page,
            label=kwargs.get("label"),
            name=kwargs.get("name"),
            selector=kwargs.get("selector"),
        )
        if locator is None:
            selects = page.locator("select")
            if await selects.count() == 0:
                return SkillResult(success=False, message="No dropdown found on page")
            locator = selects.first

        tag = await locator.evaluate("el => el.tagName.toLowerCase()")
        if tag == "select":
            await locator.select_option(label=str(value))
        else:
            await locator.click()
            option = page.get_by_role("option", name=str(value))
            if await option.count() == 0:
                option = page.get_by_text(str(value))
            if await option.count() == 0:
                return SkillResult(success=False, message=f"Option '{value}' not found")
            await option.first.click()

        return SkillResult(
            success=True,
            message=f"Selected dropdown value",
            data={"value": str(value)},
        )
