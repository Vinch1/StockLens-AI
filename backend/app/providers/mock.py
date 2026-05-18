from __future__ import annotations

from datetime import UTC, datetime, timedelta
from math import sin
from random import Random

from app.models import FundamentalMetrics, FundamentalsSummary, NewsItem, NewsSummary, OHLCVBar


class MockMarketDataProvider:
    mode = "mock"

    def get_ohlcv(self, ticker: str, timeframe: str = "1D", bars: int = 260) -> list[OHLCVBar]:
        seed = sum(ord(char) for char in ticker.upper() + timeframe)
        rng = Random(seed)
        base_price = 80 + (seed % 90)
        interval_days = 7 if timeframe == "1W" else 1
        now = datetime.now(UTC).replace(microsecond=0)
        data: list[OHLCVBar] = []
        close = float(base_price)
        for index in range(bars):
            drift = 0.045 + (0.025 * sin(index / 18))
            noise = rng.uniform(-1.2, 1.2)
            previous_close = close
            close = max(5.0, previous_close + drift + noise)
            high = max(previous_close, close) + rng.uniform(0.2, 2.4)
            low = min(previous_close, close) - rng.uniform(0.2, 2.2)
            open_price = previous_close + rng.uniform(-0.9, 0.9)
            volume = int(1_500_000 + (seed % 8) * 300_000 + rng.randint(-180_000, 280_000) + index * 900)
            timestamp = (now - timedelta(days=(bars - index - 1) * interval_days)).isoformat()
            data.append(
                OHLCVBar(
                    timestamp=timestamp,
                    open=round(open_price, 2),
                    high=round(high, 2),
                    low=round(low, 2),
                    close=round(close, 2),
                    volume=max(10_000, volume),
                )
            )
        return data

    def status(self) -> dict[str, object]:
        return {"name": "market_data", "mode": "mock", "configured": True, "message": "Demo OHLCV data is generated deterministically."}


class MockNewsProvider:
    mode = "mock"

    def get_news(self, ticker: str) -> NewsSummary:
        now = datetime.now(UTC).replace(microsecond=0)
        items = [
            NewsItem(
                title=f"Demo headline: {ticker} reports mixed quarterly update",
                source="Mock News",
                published_at=(now - timedelta(hours=8)).isoformat(),
                url=None,
                sentiment="neutral",
                catalyst_type="earnings",
                summary="Demo-only headline for UI development; configure a live news provider for real headlines.",
            ),
            NewsItem(
                title=f"Demo headline: sector volatility remains a risk for {ticker}",
                source="Mock News",
                published_at=(now - timedelta(days=1)).isoformat(),
                url=None,
                sentiment="negative",
                catalyst_type="macro",
                summary="Mock macro context highlights uncertainty without asserting a future direction.",
            ),
            NewsItem(
                title=f"Demo headline: analysts discuss product roadmap for {ticker}",
                source="Mock News",
                published_at=(now - timedelta(days=2)).isoformat(),
                url=None,
                sentiment="positive",
                catalyst_type="product",
                summary="Mock product catalyst for demonstration; it should not be treated as live news.",
            ),
        ]
        return NewsSummary(
            sentiment="mixed",
            score=-5,
            items=items,
            summary="Recent demo headlines are mixed. No current live news is configured; configure a live provider for real data.",
        )

    def status(self) -> dict[str, object]:
        return {"name": "news", "mode": "mock", "configured": False, "message": "Live news is not configured; mock demo headlines are labeled."}


class MockFundamentalsProvider:
    mode = "mock"

    def get_fundamentals(self, ticker: str) -> FundamentalsSummary:
        return FundamentalsSummary(
            quality="unavailable",
            score=50,
            metrics=FundamentalMetrics(),
            summary=(
                "Fundamental provider is not configured; using placeholder demo analysis. "
                "Technical indicators alone are not enough for long-term investing. Review fundamentals, valuation, risk tolerance, and professional guidance."
            ),
        )

    def status(self) -> dict[str, object]:
        return {"name": "fundamentals", "mode": "mock", "configured": False, "message": "Live fundamentals are not configured."}


market_provider = MockMarketDataProvider()
news_provider = MockNewsProvider()
fundamentals_provider = MockFundamentalsProvider()
