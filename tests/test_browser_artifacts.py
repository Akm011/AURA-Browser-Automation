from pathlib import Path

import pytest

from aura_browser.screenshots import ScreenshotService
from aura_browser.sessions import SessionManager, session_key


class FakePage:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def screenshot(self, **kwargs: object) -> None:
        self.calls.append(kwargs)


def test_session_manager_uses_safe_state_file_names(tmp_path: Path) -> None:
    manager = SessionManager(tmp_path)

    path = manager.state_path("finance portal/2026")

    assert path == tmp_path / "finance-portal-2026.json"
    with pytest.raises(ValueError, match="session_id"):
        session_key("---")


def test_session_manager_loads_existing_storage_state(tmp_path: Path) -> None:
    manager = SessionManager(tmp_path)
    path = manager.state_path("demo")
    path.write_text("{}", encoding="utf-8")

    assert manager.context_options("demo") == {"storage_state": str(path)}
    assert manager.context_options(None) == {}


def test_session_manager_remembers_last_url_and_completed_skills(tmp_path: Path) -> None:
    manager = SessionManager(tmp_path)

    manager.record_completion(
        "demo",
        url="https://example.com/reports",
        skills=["Navigate", "ClickElement"],
        success=True,
    )

    memory = manager.load_memory("demo")
    assert memory["last_url"] == "https://example.com/reports"
    assert memory["completed_tasks"][0]["skills"] == ["Navigate", "ClickElement"]
    assert memory["completed_tasks"][0]["success"] is True


@pytest.mark.asyncio
async def test_screenshot_service_creates_a_session_artifact_path(tmp_path: Path) -> None:
    page = FakePage()
    service = ScreenshotService(tmp_path)

    path = await service.capture(page, session_id="demo session", label="final page")

    assert Path(path).parent == tmp_path / "demo-session"
    assert Path(path).name.startswith("final-page-")
    assert page.calls == [{"path": path, "full_page": True}]
