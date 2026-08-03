from aura_models.config import AuraSettings


def test_settings_defaults() -> None:
    settings = AuraSettings()
    assert settings.app_name == "AURA Browser Intelligence Core"
    assert settings.app_version == "0.0.1"
    assert settings.browser_headless is True
    assert settings.browser_timeout_ms == 30_000


def test_settings_ensure_directories(tmp_path) -> None:
    settings = AuraSettings(
        screenshots_dir=tmp_path / "screenshots",
        downloads_dir=tmp_path / "downloads",
        logs_dir=tmp_path / "logs",
    )
    settings.ensure_directories()
    assert settings.screenshots_dir.exists()
    assert settings.downloads_dir.exists()
    assert settings.logs_dir.exists()
