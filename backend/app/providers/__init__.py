from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.providers.errors import ProviderDataError
from app.providers.protocols import ExplanationProvider, FundamentalsProvider, MarketDataProvider, NewsProvider


class _UnavailableProvider:
    """Placeholder that raises when called — used when a provider is not configured."""

    def __init__(self, name: str, reason: str) -> None:
        self._name = name
        self._reason = reason
        self.mode = "unavailable"

    async def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        raise ProviderDataError(f"{self._name} is not configured: {self._reason}")

    def status(self) -> dict[str, object]:
        return {"name": self._name, "mode": "unavailable", "configured": False, "message": self._reason}


def _create_market_provider(settings: Settings) -> MarketDataProvider:
    if settings.MARKET_DATA_PROVIDER == "yfinance":
        from app.providers.yfinance_provider import YFinanceMarketDataProvider
        return YFinanceMarketDataProvider()
    raise ValueError(f"Unknown market data provider: {settings.MARKET_DATA_PROVIDER!r}")


def _create_news_provider(settings: Settings) -> NewsProvider:
    if settings.NEWS_PROVIDER == "finnhub":
        if not settings.NEWS_API_KEY:
            return _UnavailableProvider("news", "NEWS_API_KEY is required for finnhub")
        from app.providers.finnhub_news_provider import FinnhubNewsProvider
        return FinnhubNewsProvider(api_key=settings.NEWS_API_KEY)
    raise ValueError(f"Unknown news provider: {settings.NEWS_PROVIDER!r}")


def _create_fundamentals_provider(settings: Settings) -> FundamentalsProvider:
    if settings.FUNDAMENTALS_PROVIDER == "yfinance":
        from app.providers.yfinance_fundamentals_provider import YFinanceFundamentalsProvider
        return YFinanceFundamentalsProvider()
    raise ValueError(f"Unknown fundamentals provider: {settings.FUNDAMENTALS_PROVIDER!r}")


def _create_explanation_provider(settings: Settings) -> ExplanationProvider | None:
    if settings.AI_PROVIDER and settings.AI_API_KEY:
        from app.providers.ai_explanation_provider import AIExplanationProvider
        return AIExplanationProvider(
            api_key=settings.AI_API_KEY,
            model=settings.AI_MODEL,
            provider=settings.AI_PROVIDER,
        )
    return None


@dataclass
class Providers:
    market: MarketDataProvider
    news: NewsProvider
    fundamentals: FundamentalsProvider
    explanation: ExplanationProvider | None


def create_providers(settings: Settings) -> Providers:
    return Providers(
        market=_create_market_provider(settings),
        news=_create_news_provider(settings),
        fundamentals=_create_fundamentals_provider(settings),
        explanation=_create_explanation_provider(settings),
    )
