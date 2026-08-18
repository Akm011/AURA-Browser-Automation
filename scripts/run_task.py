#!/usr/bin/env python3
"""Run a natural-language browser task through the AURA planner and executor."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from aura_browser import BrowserManager, configure_logging
from aura_models.config import get_settings
from aura_planner import PlannerAgent
from aura_skills import ActionExecutor


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="AURA – plan and execute a natural-language browser task"
    )
    parser.add_argument("request", help='Task request, e.g. "Open https://example.com and click More information"')
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")
    parser.add_argument("--plan-only", action="store_true", help="Only show the generated plan")
    args = parser.parse_args()

    settings = get_settings()
    if args.headed:
        settings.browser_headless = False

    configure_logging(settings)

    agent = PlannerAgent()
    plan = agent.plan(args.request)

    if args.plan_only:
        print(json.dumps(plan.model_dump(mode="json"), indent=2))
        return 0

    executor = ActionExecutor(settings=settings)

    async with BrowserManager(settings).session() as browser:
        page = await browser.new_page()
        result = await executor.execute_plan(plan, page)

    print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
