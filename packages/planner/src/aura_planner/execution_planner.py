from __future__ import annotations

from aura_models.planning import ExecutionPlan, ParsedIntent, PlanStep
from aura_skills.executor import ActionExecutor


class ExecutionPlanner:
    """Maps parsed intent to an ordered list of browser skill steps."""

    def plan(self, intent: ParsedIntent) -> ExecutionPlan:
        if intent.proposed_steps:
            return ExecutionPlan(
                request=intent.raw_request,
                steps=[PlanStep.model_validate(step) for step in intent.proposed_steps],
            )

        steps: list[PlanStep] = []

        if intent.target_url:
            steps.append(
                PlanStep(
                    skill=ActionExecutor.NAVIGATE_SKILL,
                    params={"url": intent.target_url},
                    description=f"Open {intent.target_url}",
                )
            )

        for action in intent.actions:
            if action == "navigate" and intent.target_url:
                continue
            steps.extend(self._steps_for_action(action, intent))

        if not steps and intent.target_url:
            steps.append(
                PlanStep(
                    skill=ActionExecutor.NAVIGATE_SKILL,
                    params={"url": intent.target_url},
                    description=f"Open {intent.target_url}",
                )
            )

        return ExecutionPlan(request=intent.raw_request, steps=steps)

    def _steps_for_action(self, action: str, intent: ParsedIntent) -> list[PlanStep]:
        if action == "login":
            if not intent.credentials_provided:
                return []
            return [
                PlanStep(
                    skill="FindLoginForm",
                    params={},
                    description="Locate login form fields",
                ),
                PlanStep(
                    skill="FillInput",
                    params={
                        "selector": "input[type='email'], input[type='text']",
                        "value": intent.entities["username"],
                    },
                    description="Fill username or email",
                ),
                PlanStep(
                    skill="FillInput",
                    params={
                        "selector": "input[type='password']",
                        "value": intent.entities["password"],
                    },
                    description="Fill password",
                ),
                PlanStep(
                    skill="ClickElement",
                    params={"selector": "button[type='submit'], input[type='submit']"},
                    description="Submit login form",
                ),
            ]

        if action == "click":
            target = intent.entities.get("click_target") or intent.entities.get("quoted_text")
            if not target:
                return []
            return [
                PlanStep(
                    skill="ClickElement",
                    params={"text": target},
                    description=f"Click '{target}'",
                )
            ]

        if action == "search":
            query = intent.entities.get("search_query") or intent.entities.get("quoted_text", "")
            return [
                PlanStep(
                    skill="FindSearchBar",
                    params={},
                    description="Locate search bar",
                ),
                PlanStep(
                    skill="FillInput",
                    params={
                        "selector": "input[type='search'], [role='searchbox']",
                        "value": query,
                    },
                    description="Enter search query",
                ),
                PlanStep(
                    skill="ClickElement",
                    params={"selector": "button[type='submit'], [aria-label*='search' i]"},
                    description="Submit search",
                ),
            ]

        if action == "select":
            value = intent.entities.get("quoted_text") or intent.entities.get("secondary_text")
            if not value:
                return []
            return [
                PlanStep(
                    skill="SelectDropdown",
                    params={"value": value},
                    description=f"Select '{value}' from dropdown",
                )
            ]

        if action == "menu":
            path_text = intent.entities.get("menu_path") or intent.entities.get("quoted_text")
            if not path_text:
                return []
            path = [part.strip() for part in path_text.split(">")]
            return [
                PlanStep(
                    skill="NavigateMenu",
                    params={"path": path},
                    description=f"Navigate menu: {' > '.join(path)}",
                )
            ]

        if action == "fill":
            value = intent.entities.get("quoted_text", "")
            label = intent.entities.get("secondary_text")
            params: dict = {"value": value}
            if label:
                params["label"] = label
            return [
                PlanStep(
                    skill="FillInput",
                    params=params,
                    description="Fill input field",
                )
            ]

        if action == "wait":
            raw_seconds = intent.entities.get("wait_seconds")
            if not raw_seconds:
                return []
            seconds = float(raw_seconds)
            return [
                PlanStep(
                    skill="Wait",
                    params={"seconds": seconds},
                    description=f"Wait for {seconds} seconds",
                )
            ]

        if action == "download":
            target = intent.entities.get("download_target") or intent.entities.get("quoted_text")
            return [
                PlanStep(
                    skill="DownloadFile",
                    params={"text": target} if target else {},
                    description="Download requested file",
                )
            ]

        if action == "extract":
            return [
                PlanStep(skill="ExtractText", params={}, description="Extract visible page text")
            ]

        if action == "scroll":
            return [PlanStep(skill="ScrollPage", params={}, description="Scroll the page")]

        if action == "press":
            key = intent.entities.get("key") or intent.entities.get("quoted_text")
            return [
                PlanStep(skill="PressKey", params={"key": key} if key else {}, description="Press key")
            ]

        return []
