from __future__ import annotations

import re

from aura_models.planning import ParsedIntent

URL_PATTERN = re.compile(r"https?://[^\s,]+", re.I)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\((https?://[^\s)]+)\)", re.I)
QUOTED_TEXT = re.compile(r"['\"]([^'\"]+)['\"]")
WAIT_PATTERN = re.compile(
    r"wait(?:\s+for)?\s+(\d+(?:\.\d+)?)\s*(seconds?|secs?|s|minutes?|mins?|m)\b",
    re.I,
)


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
        "wait": "wait",
    }

    def parse(self, request: str) -> ParsedIntent:
        normalized = request.strip()
        markdown_link_match = MARKDOWN_LINK_PATTERN.search(normalized)
        url_match = markdown_link_match or URL_PATTERN.search(normalized)
        if markdown_link_match:
            target_url = markdown_link_match.group(1)
        else:
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
        matches: list[tuple[int, str, str]] = []

        for keyword, action in self.ACTION_KEYWORDS.items():
            start = 0
            while True:
                idx = lowered.find(keyword, start)
                if idx < 0:
                    break
                matches.append((idx, len(keyword), action))
                start = idx + len(keyword)

        matches.sort(key=lambda item: item[0])

        found: list[str] = []
        for _, _, action in matches:
            if action not in found:
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

        wait_match = WAIT_PATTERN.search(text)
        if wait_match:
            entities["wait_seconds"] = str(
                self._parse_duration(wait_match.group(1), wait_match.group(2))
            )

        click_match = re.search(
            r"click(?: on)?\s+(.+?)(?:\s+and\s+wait\b|\s+wait\b|\.\s|,|$)",
            text,
            re.I,
        )
        if click_match and "click_target" not in entities:
            target = click_match.group(1).strip().strip("'\"")
            target = re.split(r"\s+and\s+wait\b", target, maxsplit=1, flags=re.I)[0].strip()
            if target:
                entities["click_target"] = target

        search_match = re.search(r"search(?: for)?\s+(.+?)(?:\.|,|$)", text, re.I)
        if search_match:
            entities["search_query"] = search_match.group(1).strip().strip("'\"")

        # Do not include "open" here: in requests such as "Open <URL> and
        # navigate to Reports menu", matching from the first word would absorb
        # the URL and every intervening action.
        menu_match = re.search(r"(?:navigate to|go to)\s+(.+?)\s+menu", text, re.I)
        if menu_match:
            entities["menu_path"] = menu_match.group(1).strip()

        return entities

    @staticmethod
    def _parse_duration(value: str, unit: str) -> float:
        seconds = float(value)
        if unit.lower().startswith("m"):
            seconds *= 60
        return seconds
