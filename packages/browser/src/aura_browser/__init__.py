"""Playwright browser execution engine."""

from aura_browser.logging import configure_logging, get_logger
from aura_browser.manager import BrowserManager

__all__ = ["BrowserManager", "configure_logging", "get_logger"]
