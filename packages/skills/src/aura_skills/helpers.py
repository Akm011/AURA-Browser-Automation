from __future__ import annotations

import re

from playwright.async_api import Locator, Page


async def resolve_locator(page: Page, *, text: str | None = None, selector: str | None = None) -> Locator | None:
    if selector:
        locator = page.locator(selector)
        if await locator.count() > 0:
            return locator.first
        return None

    if not text:
        return None

    strategies: list[Locator] = [
        page.get_by_role("button", name=re.compile(re.escape(text), re.I)),
        page.get_by_role("link", name=re.compile(re.escape(text), re.I)),
        page.get_by_role("menuitem", name=re.compile(re.escape(text), re.I)),
        page.get_by_label(re.compile(re.escape(text), re.I)),
        page.get_by_placeholder(re.compile(re.escape(text), re.I)),
        page.get_by_text(re.compile(re.escape(text), re.I)),
    ]

    for locator in strategies:
        if await locator.count() > 0:
            return locator.first

    return None


async def resolve_input(
    page: Page,
    *,
    label: str | None = None,
    placeholder: str | None = None,
    name: str | None = None,
    selector: str | None = None,
) -> Locator | None:
    if selector:
        locator = page.locator(selector)
        if await locator.count() > 0:
            return locator.first

    for key, value in (("label", label), ("placeholder", placeholder), ("name", name)):
        if not value:
            continue
        if key == "label":
            locator = page.get_by_label(re.compile(re.escape(value), re.I))
        elif key == "placeholder":
            locator = page.get_by_placeholder(re.compile(re.escape(value), re.I))
        else:
            locator = page.locator(f"[name='{value}']")
        if await locator.count() > 0:
            return locator.first

    return None
