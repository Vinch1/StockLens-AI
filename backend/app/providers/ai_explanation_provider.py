from __future__ import annotations

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

    def generate_conclusion(
        self,
        setup: str,
        score: int,
        confidence: str,
        news_summary: str = "",
        fundamentals_summary: str = "",
    ) -> str:
        system_prompt = (
            "You are an educational stock research summarizer. You do NOT provide investment advice, "
            "financial advice, or trading instructions.\n\n"
            "Rules:\n"
            '- Never use phrases like: "buy now", "sell now", "guaranteed", "risk-free", '
            '"sure profit", "this stock will", "you should invest", "all in", "100%", '
            '"can\'t lose", "secret signal"\n'
            '- Use only these terms: "research candidate", "watchlist candidate", '
            '"mixed setup", "high-risk setup", "needs more confirmation"\n'
            '- Always include: "This is educational information only, not financial advice."\n'
            "- Keep response to 3-4 sentences maximum\n"
            "- Focus on summarizing the technical setup, risks, and what further research could cover"
        )

        user_message = (
            "Analyze this stock research data and provide an educational summary:\n"
            f"- Technical setup: {setup}\n"
            f"- Overall score: {score}/100\n"
            f"- Confidence: {confidence}\n"
            f"- News context: {news_summary or 'Not included'}\n"
            f"- Fundamentals: {fundamentals_summary or 'Not included'}"
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

            response = litellm.completion(**kwargs)
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
