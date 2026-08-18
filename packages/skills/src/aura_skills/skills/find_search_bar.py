from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult


class FindSearchBar(BrowserSkill):
    name = "FindSearchBar"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        page = context.playwright_page

        candidates = [
            page.locator("input[type='search']"),
            page.get_by_role("searchbox"),
            page.locator("input[name*='search' i]"),
            page.locator("input[placeholder*='search' i]"),
            page.locator("input[aria-label*='search' i]"),
        ]

        for locator in candidates:
            if await locator.count() > 0:
                return SkillResult(
                    success=True,
                    message="Search bar located",
                    data={"found": True, "count": await locator.count()},
                )

        return SkillResult(success=False, message="No search bar found on page")
