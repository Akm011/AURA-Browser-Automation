from __future__ import annotations

from aura_models.planning import ExecutionPlan, PlanExecutionResult
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
        plan.requires_approval, plan.approval_reason = self._approval_requirement(plan)
        return plan

    @staticmethod
    def validate_result(result: PlanExecutionResult) -> dict[str, object]:
        completed = len(result.step_results)
        return {
            "valid": result.success and all(step.success for step in result.step_results),
            "completed_steps": completed,
            "failed_step": next(
                (step.step_index for step in result.step_results if not step.success), None
            ),
        }

    @staticmethod
    def _approval_requirement(plan: ExecutionPlan) -> tuple[bool, str | None]:
        if any(step.skill == "UploadFile" for step in plan.steps):
            return True, "Uploading a file requires approval."
        password_entered = any(
            step.skill == "FillInput" and "password" in str(step.params.get("selector", "")).lower()
            for step in plan.steps
        )
        form_submit = any(
            step.skill == "ClickElement" and "submit" in str(step.params.get("selector", "")).lower()
            for step in plan.steps
        )
        if password_entered and form_submit:
            return True, "Submitting login credentials requires approval."
        return False, None
