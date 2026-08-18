from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult


class FindLoginForm(BrowserSkill):
    name = "FindLoginForm"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        page = context.playwright_page

        password = page.locator("input[type='password']")
        if await password.count() == 0:
            return SkillResult(success=False, message="No password field found on page")

        password_input = password.first
        form = password_input.locator("xpath=ancestor::form[1]")
        scope = form if await form.count() > 0 else page

        username = scope.locator(
            "input[type='email'], input[type='text'], input[name*='user' i], "
            "input[name*='email' i], input[name*='login' i], input[autocomplete='username']"
        )
        submit = scope.locator(
            "button[type='submit'], input[type='submit'], button:has-text('log in'), "
            "button:has-text('login'), button:has-text('sign in')"
        )

        username_count = await username.count()
        submit_count = await submit.count()

        return SkillResult(
            success=True,
            message="Login form located",
            data={
                "has_username": username_count > 0,
                "has_password": True,
                "has_submit": submit_count > 0,
                "username_selector": "input[type='email'], input[type='text']" if username_count else None,
                "password_selector": "input[type='password']",
                "submit_selector": "button[type='submit'], input[type='submit']" if submit_count else None,
            },
        )
