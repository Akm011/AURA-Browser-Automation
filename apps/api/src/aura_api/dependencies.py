from __future__ import annotations

from aura_execution import BrowserExecutionService
from aura_models.config import AuraSettings, get_settings

_execution_service: BrowserExecutionService | None = None


def get_execution_service() -> BrowserExecutionService:
    global _execution_service
    if _execution_service is None:
        _execution_service = BrowserExecutionService(settings=get_settings())
    return _execution_service


def reset_execution_service() -> None:
    global _execution_service
    _execution_service = None
