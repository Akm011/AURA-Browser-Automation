from __future__ import annotations

from aura_models.planning import ExecutionPlan
from aura_skills import ActionExecutor, default_registry


class PlanValidator:
    """Reject plans that cannot be executed before a browser is opened."""

    def validate(self, plan: ExecutionPlan) -> ExecutionPlan:
        available = set(default_registry().list_names()) | {ActionExecutor.NAVIGATE_SKILL, "Wait"}
        for step in plan.steps:
            if step.skill not in available:
                raise ValueError(f"Unknown skill in plan: {step.skill}")
            if step.skill == "Navigate" and not step.params.get("url"):
                raise ValueError("Navigate step requires url param")
            if step.skill == "Wait" and step.params.get("seconds") is None:
                raise ValueError("Wait step requires seconds param")
        return plan
