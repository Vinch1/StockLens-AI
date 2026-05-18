from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.providers.protocols import ExplanationProvider, FundamentalsProvider, MarketDataProvider, NewsProvider


def _create_market_provider(settings: Settings) -> MarketDataProvider:
    if settings.MARKET_DATA_PROVIDER == "yfinance":
        from app.providers.yfinance_provider import YFinanceMarketDataProvider

        return YFinanceMarketDataProvider()
    from app.providers.mock import MockMarketDataProvider

    return MockMarketDataProvider()


def _create_news_provider(settings: Settings) -> NewsProvider:
    if settings.NEWS_PROVIDER == "finnhub" and settings.NEWS_API_KEY:
        from app.providers.finnhub_news_provider import FinnhubNewsProvider

        return FinnhubNewsProvider(api_key=settings.NEWS_API_KEY)
    from app.providers.mock import MockNewsProvider

    return MockNewsProvider()


def _create_fundamentals_provider(settings: Settings) -> FundamentalsProvider:
    if settings.FUNDAMENTALS_PROVIDER == "yfinance":
        from app.providers.yfinance_fundamentals_provider import YFinanceFundamentalsProvider

        return YFinanceFundamentalsProvider()
    from app.providers.mock import MockFundamentalsProvider

    return MockFundamentalsProvider()


def _create_explanation_provider(settings: Settings) -> ExplanationProvider | None:
    if settings.AI_PROVIDER != "mock" and settings.AI_API_KEY:
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
    if settings.MOCK_MODE:
        from app.providers.mock import (
            MockFundamentalsProvider,
            MockMarketDataProvider,
            MockNewsProvider,
        )

        return Providers(
            market=MockMarketDataProvider(),
            news=MockNewsProvider(),
            fundamentals=MockFundamentalsProvider(),
            explanation=None,
        )

    return Providers(
        market=_create_market_provider(settings),
        news=_create_news_provider(settings),
        fundamentals=_create_fundamentals_provider(settings),
        explanation=_create_explanation_provider(settings),
    )
