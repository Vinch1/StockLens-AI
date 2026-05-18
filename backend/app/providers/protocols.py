from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.models import FundamentalsSummary, NewsSummary, OHLCVBar


@runtime_checkable
class MarketDataProvider(Protocol):
    mode: str

    async def get_ohlcv(self, ticker: str, timeframe: str = "1D", bars: int = 260) -> list[OHLCVBar]: ...

    def status(self) -> dict[str, object]: ...


@runtime_checkable
class NewsProvider(Protocol):
    mode: str

    async def get_news(self, ticker: str) -> NewsSummary: ...

    def status(self) -> dict[str, object]: ...


@runtime_checkable
class FundamentalsProvider(Protocol):
    mode: str

    async def get_fundamentals(self, ticker: str) -> FundamentalsSummary: ...

    def status(self) -> dict[str, object]: ...


@runtime_checkable
class ExplanationProvider(Protocol):
    mode: str

    async def generate_conclusion(
        self,
        setup: str,
        score: int,
        confidence: str,
        news_summary: str = "",
        fundamentals_summary: str = "",
    ) -> str: ...

    def status(self) -> dict[str, object]: ...
