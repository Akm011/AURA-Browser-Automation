from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from aura_browser.logging import get_logger
from aura_models.config import AuraSettings, get_settings
from aura_models.execution import BrowserSession, LaunchResult

logger = get_logger(__name__)


class BrowserManager:
    """Manages Playwright browser lifecycle and URL navigation."""

    def __init__(self, settings: AuraSettings | None = None) -> None:
        self.settings = settings or get_settings()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def start(self) -> None:
        if self._browser is not None:
            return

        logger.info(
            "browser.starting",
            headless=self.settings.browser_headless,
            timeout_ms=self.settings.browser_timeout_ms,
        )
        self._playwright = await async_playwright().start()
        launch_kwargs: dict = {
            "headless": self.settings.browser_headless,
            "slow_mo": self.settings.browser_slow_mo_ms,
        }
        if self.settings.browser_channel:
            launch_kwargs["channel"] = self.settings.browser_channel

        self._browser = await self._playwright.chromium.launch(**launch_kwargs)
        self._context = await self._browser.new_context(
            accept_downloads=True,
            viewport={"width": 1280, "height": 720},
        )
        self._context.set_default_timeout(self.settings.browser_timeout_ms)
        logger.info("browser.started")

    async def stop(self) -> None:
        if self._context is not None:
            await self._context.close()
            self._context = None
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None
        logger.info("browser.stopped")

    @asynccontextmanager
    async def session(self) -> AsyncIterator[BrowserManager]:
        await self.start()
        try:
            yield self
        finally:
            await self.stop()

    async def new_page(self) -> Page:
        if self._context is None:
            await self.start()
        assert self._context is not None
        return await self._context.new_page()

    async def launch_url(self, url: str, *, screenshot: bool = True) -> LaunchResult:
        session_id = str(uuid.uuid4())
        page: Page | None = None

        try:
            page = await self.new_page()
            logger.info("browser.navigate", url=url, session_id=session_id)
            response = await page.goto(url, wait_until="domcontentloaded")

            if response is None or not response.ok:
                status = response.status if response else "no_response"
                raise RuntimeError(f"Navigation failed with status: {status}")

            title = await page.title()
            browser_session = BrowserSession(session_id=session_id, url=url, title=title)

            screenshot_path: str | None = None
            if screenshot:
                screenshot_path = str(
                    self.settings.screenshots_dir / f"{session_id}.png"
                )
                await page.screenshot(path=screenshot_path, full_page=True)
                logger.info("browser.screenshot", path=screenshot_path)

            logger.info(
                "browser.launch_success",
                session_id=session_id,
                title=title,
                url=url,
            )
            return LaunchResult(
                success=True,
                session=browser_session,
                screenshot_path=screenshot_path,
            )
        except Exception as exc:
            logger.exception("browser.launch_failed", session_id=session_id, url=url)
            return LaunchResult(success=False, error=str(exc))
        finally:
            if page is not None:
                await page.close()
