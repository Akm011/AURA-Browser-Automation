from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult
from aura_skills.helpers import resolve_locator


class NavigateMenu(BrowserSkill):
    name = "NavigateMenu"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        page = context.playwright_page
        path: list[str] = kwargs.get("path") or []
        if not path and kwargs.get("text"):
            path = [kwargs["text"]]
        if not path:
            return SkillResult(success=False, message="Missing menu path or text")

        visited: list[str] = []
        for item in path:
            locator = await resolve_locator(page, text=item)
            if locator is None:
                return SkillResult(
                    success=False,
                    message=f"Menu item not found: {item}",
                    data={"visited": visited},
                )
            await locator.click()
            visited.append(item)

        return SkillResult(
            success=True,
            message="Menu navigation completed",
            data={"path": visited},
        )
