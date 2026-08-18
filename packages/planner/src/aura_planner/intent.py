from __future__ import annotations

import re

from aura_models.planning import ParsedIntent

URL_PATTERN = re.compile(r"https?://[^\s,]+", re.I)
QUOTED_TEXT = re.compile(r"['\"]([^'\"]+)['\"]")


class IntentParser:
    """Extracts structured intent from natural-language browser requests."""

    ACTION_KEYWORDS = {
        "login": "login",
        "log in": "login",
        "sign in": "login",
        "click": "click",
        "fill": "fill",
        "search": "search",
        "navigate": "navigate",
        "go to": "navigate",
        "open": "navigate",
        "select": "select",
        "download": "download",
        "menu": "menu",
    }

    def parse(self, request: str) -> ParsedIntent:
        normalized = request.strip()
        url_match = URL_PATTERN.search(normalized)
        target_url = url_match.group(0).rstrip(".,)") if url_match else None

        actions = self._detect_actions(normalized)
        entities = self._extract_entities(normalized)

        goal = normalized
        if target_url:
            goal = normalized.replace(target_url, "").strip(" ,")

        return ParsedIntent(
            raw_request=normalized,
            target_url=target_url,
            goal=goal or normalized,
            actions=actions,
            entities=entities,
        )

    def _detect_actions(self, text: str) -> list[str]:
        lowered = text.lower()
        found: list[str] = []
        for keyword, action in self.ACTION_KEYWORDS.items():
            if keyword in lowered and action not in found:
                found.append(action)
        if not found:
            found.append("navigate")
        return found

    def _extract_entities(self, text: str) -> dict[str, str]:
        entities: dict[str, str] = {}
        quoted = QUOTED_TEXT.findall(text)
        if quoted:
            entities["quoted_text"] = quoted[0]
            if len(quoted) > 1:
                entities["secondary_text"] = quoted[1]

        click_match = re.search(r"click(?: on)?\s+(.+?)(?:\.|,|$)", text, re.I)
        if click_match and "click_target" not in entities:
            target = click_match.group(1).strip().strip("'\"")
            if target:
                entities["click_target"] = target

        search_match = re.search(r"search(?: for)?\s+(.+?)(?:\.|,|$)", text, re.I)
        if search_match:
            entities["search_query"] = search_match.group(1).strip().strip("'\"")

        menu_match = re.search(r"(?:navigate to|go to|open)\s+(.+?)\s+menu", text, re.I)
        if menu_match:
            entities["menu_path"] = menu_match.group(1).strip()

        return entities
