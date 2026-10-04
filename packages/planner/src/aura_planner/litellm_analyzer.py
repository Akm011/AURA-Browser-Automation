from __future__ import annotations

from typing import Any, Callable

from aura_models.config import AuraSettings

from aura_planner.request_analyzer import (
    PLANNER_RESPONSE_SCHEMA,
    SYSTEM_PROMPT,
    OpenAIRequestAnalyzer,
)


class LiteLLMRequestAnalyzer(OpenAIRequestAnalyzer):
    """Provider-neutral structured request analysis through LiteLLM."""

    def __init__(
        self,
        *,
        settings: AuraSettings,
        completion: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(settings=settings, **kwargs)
        self._completion = completion

    def analyze(self, request: str):
        if not (self.settings.litellm_api_key or self.settings.openai_api_key):
            return self._fallback(request)
        try:
            response = self._get_completion()(
                model=self.settings.litellm_model,
                api_key=self.settings.litellm_api_key or self.settings.openai_api_key,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": request},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "browser_execution_plan",
                        "schema": PLANNER_RESPONSE_SCHEMA,
                        "strict": True,
                    },
                },
            )
            output = response.choices[0].message.content
            if not isinstance(output, str):
                raise ValueError("LiteLLM returned no structured content")
            return self._to_intent(request, output)
        except Exception:
            return self._fallback(request)

    def _get_completion(self) -> Callable[..., Any]:
        if self._completion is None:
            from litellm import completion

            self._completion = completion
        return self._completion
