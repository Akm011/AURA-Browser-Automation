from aura_models.config import AuraSettings


def test_settings_defaults() -> None:
    # Do not allow a developer's local .env file to change the expected defaults.
    settings = AuraSettings(_env_file=None)
    assert settings.app_name == "AURA Browser Intelligence Core"
    assert settings.app_version == "0.2.1"
    assert settings.browser_headless is True
    assert settings.browser_timeout_ms == 30_000
    assert settings.browser_step_delay_seconds == 0


def test_settings_ensure_directories(tmp_path) -> None:
    settings = AuraSettings(
        screenshots_dir=tmp_path / "screenshots",
        sessions_dir=tmp_path / "sessions",
        downloads_dir=tmp_path / "downloads",
        logs_dir=tmp_path / "logs",
    )
    settings.ensure_directories()
    assert settings.screenshots_dir.exists()
    assert settings.sessions_dir.exists()
    assert settings.downloads_dir.exists()
    assert settings.logs_dir.exists()
