from __future__ import annotations

from app.providers.litellm_logging import suppress_litellm_optional_dependency_warnings

suppress_litellm_optional_dependency_warnings()

import litellm

from app.providers.errors import ProviderError, ProviderUnavailableError


class AIExplanationProvider:
    mode = "live"

    def __init__(self, api_key: str, model: str, provider: str) -> None:
        self.api_key = api_key
        self.model = model
        self.provider = provider

        if provider == "openai":
            self._litellm_model = model
        elif provider == "anthropic":
            self._litellm_model = f"anthropic/{model}"
        elif provider == "glm":
            self._litellm_model = f"zai/{model}"
            self._api_base = "https://api.z.ai/api/coding/paas/v4"
        elif provider == "openrouter":
            self._litellm_model = f"openrouter/{model}"
        else:
            self._litellm_model = model

    async def generate_conclusion(
        self,
        setup: str,
        score: int,
        confidence: str,
        news_summary: str = "",
        fundamentals_summary: str = "",
    ) -> str:
        system_prompt = (
            "You summarize structured stock research data for an app report.\n"
            "Use only the values provided by the user message. Do not invent prices, news, "
            "fundamental metrics, events, certainty, or future outcomes.\n\n"
            "Output rules:\n"
            "- Return plain text only, not Markdown, JSON, bullets, or headings.\n"
            "- Write 2 to 4 concise sentences.\n"
            "- Mention the setup, score, and confidence.\n"
            "- Mention news and fundamentals only when they are included.\n"
            "- Include the main risk or uncertainty when confidence is low or signals are mixed.\n"
            "- Do not give instructions about position sizing, brokerage actions, or portfolio allocation."
        )

        user_message = (
            "Summarize this stock research data:\n"
            f"- Technical setup: {setup}\n"
            f"- Overall score: {score}/100\n"
            f"- Confidence: {confidence}\n"
            f"- News context: {news_summary or 'Not included'}\n"
            f"- Fundamentals: {fundamentals_summary or 'Not included'}\n\n"
            "If a field says 'Not included', do not discuss that section."
        )

        try:
            kwargs: dict[str, object] = {
                "model": self._litellm_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 200,
                "temperature": 0.3,
                "api_key": self.api_key,
            }
            if self.provider == "glm":
                kwargs["api_base"] = self._api_base

            response = await litellm.acompletion(**kwargs)
            return response.choices[0].message.content
        except litellm.exceptions.AuthenticationError as exc:
            raise ProviderUnavailableError(str(exc)) from exc
        except litellm.exceptions.APIConnectionError as exc:
            raise ProviderUnavailableError(str(exc)) from exc
        except litellm.exceptions.RateLimitError as exc:
            raise ProviderUnavailableError(str(exc)) from exc
        except litellm.exceptions.APIError as exc:
            raise ProviderUnavailableError(str(exc)) from exc
        except litellm.Exception as exc:
            raise ProviderUnavailableError(str(exc)) from exc
        except Exception as exc:
            raise ProviderError(f"AI explanation generation failed: {exc}") from exc

    def status(self) -> dict[str, object]:
        return {
            "name": "ai_explanation",
            "mode": "live",
            "configured": True,
            "message": f"AI explanations via {self.provider} ({self.model}).",
        }
