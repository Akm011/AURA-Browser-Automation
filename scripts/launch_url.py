#!/usr/bin/env python3
"""Launch a URL using the AURA browser engine."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from aura_browser import BrowserManager, configure_logging
from aura_models.config import get_settings


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="AURA Browser Intelligence Core – launch any URL"
    )
    parser.add_argument("url", help="URL to open in the browser")
    parser.add_argument(
        "--no-screenshot",
        action="store_true",
        help="Skip capturing a screenshot after navigation",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode (visible window)",
    )
    args = parser.parse_args()

    settings = get_settings()
    if args.headed:
        settings.browser_headless = False

    configure_logging(settings)

    async with BrowserManager(settings).session() as browser:
        result = await browser.launch_url(
            args.url,
            screenshot=not args.no_screenshot,
        )

    print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
