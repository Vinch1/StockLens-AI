from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.providers.chart_metadata_provider import ChartMetadataProvider
from app.providers.errors import ProviderDataError
from app.providers.protocols import ExplanationProvider, FundamentalsProvider, MarketDataProvider, NewsProvider


class _UnavailableProvider:
    """Placeholder that raises when called — used when a provider is not configured."""

    def __init__(self, name: str, reason: str) -> None:
        self._name = name
        self._reason = reason
        self.mode = "unavailable"

    def _raise(self) -> None:
        raise ProviderDataError(f"{self._name} is not configured: {self._reason}")

    async def get_ohlcv(self, *args: object, **kwargs: object) -> object:
        self._raise()

    async def get_news(self, *args: object, **kwargs: object) -> object:
        self._raise()

    async def get_fundamentals(self, *args: object, **kwargs: object) -> object:
        self._raise()

    async def generate_conclusion(self, *args: object, **kwargs: object) -> str:
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


def _create_chart_metadata_provider(settings: Settings) -> ChartMetadataProvider | None:
    if settings.CHART_VISION_PROVIDER and settings.CHART_VISION_API_KEY:
        from app.providers.chart_metadata_provider import VLMChartMetadataProvider
        return VLMChartMetadataProvider(
            api_key=settings.CHART_VISION_API_KEY,
            model=settings.CHART_VISION_MODEL,
            provider=settings.CHART_VISION_PROVIDER,
        )
    return None


@dataclass
class Providers:
    market: MarketDataProvider
    news: NewsProvider
    fundamentals: FundamentalsProvider
    explanation: ExplanationProvider | None
    chart_vision: ChartMetadataProvider | None = None


def create_providers(settings: Settings) -> Providers:
    return Providers(
        market=_create_market_provider(settings),
        news=_create_news_provider(settings),
        fundamentals=_create_fundamentals_provider(settings),
        explanation=_create_explanation_provider(settings),
        chart_vision=_create_chart_metadata_provider(settings),
    )
