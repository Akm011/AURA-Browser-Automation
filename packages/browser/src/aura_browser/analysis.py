from __future__ import annotations

from typing import Any

# The embedded browser-side JavaScript is intentionally kept readable.
# ruff: noqa: E501

class DOMAnalyzer:
    """Extract a compact, semantic description of an arbitrary page."""

    async def summarize(self, page: Any) -> dict[str, Any]:
        return await page.evaluate(
            """() => {
              const clean = value => (value || '').replace(/\\s+/g, ' ').trim();
              const items = [...document.querySelectorAll('a, button, input, select, textarea, [role]')]
                .filter(el => el.getClientRects().length).slice(0, 100).map(el => ({
                  tag: el.tagName.toLowerCase(), role: el.getAttribute('role'),
                  name: clean(el.getAttribute('aria-label') || el.innerText || el.value || el.placeholder),
                  href: el instanceof HTMLAnchorElement ? el.href : null, type: el.getAttribute('type'),
                  id: el.id || null, name_attr: el.getAttribute('name')
                }));
              return {url: location.href, title: document.title,
                headings: [...document.querySelectorAll('h1, h2, h3')].map(el => clean(el.innerText)).filter(Boolean).slice(0, 20),
                elements: items, links: items.filter(item => item.href).map(({name, href}) => ({name, href}))};
            }"""
        )

    @staticmethod
    def locator_for(element: dict[str, Any]) -> dict[str, str]:
        """Prefer semantic locators before fragile CSS selectors."""
        role, name = element.get("role"), element.get("name")
        if role and name:
            return {"role": str(role), "name": str(name)}
        if element.get("id"):
            return {"selector": f"#{element['id']}"}
        if element.get("name_attr"):
            return {"selector": f"[name={element['name_attr']!r}]"}
        if name:
            return {"text": str(name)}
        return {"selector": str(element.get("tag") or "body")}


class NavigationGraphBuilder:
    """Build the current-page navigation graph from a DOM summary."""

    @staticmethod
    def build(summary: dict[str, Any]) -> dict[str, Any]:
        source = summary.get("url")
        edges = [
            {"from": source, "to": link["href"], "label": link.get("name") or link["href"]}
            for link in summary.get("links", []) if link.get("href")
        ]
        return {"nodes": [source, *[edge["to"] for edge in edges]], "edges": edges}
