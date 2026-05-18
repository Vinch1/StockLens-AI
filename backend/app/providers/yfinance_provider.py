from __future__ import annotations

import asyncio
from typing import Literal

import yfinance as yf

from app.models import OHLCVBar
from app.providers.cache import _ohlcv_cache, aget_with_cache
from app.providers.errors import ProviderDataError, ProviderError

_INTERVAL_MAP: dict[str, str] = {
    "1D": "1d",
    "1W": "1wk",
    "15m": "15m",
    "1h": "60m",
    "4h": "4h",
}

_PERIOD_MAP: dict[str, str] = {
    "15m": "60d",
    "1h": "60d",
    "4h": "60d",
    "1D": "2y",
    "1W": "5y",
}

_INTRADAY: set[str] = {"15m", "1h", "4h"}
_WEEKLY: set[str] = {"1W"}


def _cache_ttl_for_timeframe(timeframe: str) -> int:
    if timeframe in _INTRADAY:
        return 300
    if timeframe in _WEEKLY:
        return 3600
    return 900


class YFinanceMarketDataProvider:
    mode: Literal["live"] = "live"

    async def get_ohlcv(self, ticker: str, timeframe: str = "1D", bars: int = 260) -> list[OHLCVBar]:
        cache_key = (ticker, timeframe)
        ttl = _cache_ttl_for_timeframe(timeframe)
        return await aget_with_cache(_ohlcv_cache, cache_key, lambda: self._fetch_ohlcv(ticker, timeframe, bars), ttl=ttl)

    async def _fetch_ohlcv(self, ticker: str, timeframe: str, bars: int) -> list[OHLCVBar]:
        interval = _INTERVAL_MAP.get(timeframe, "1d")
        period = _PERIOD_MAP.get(timeframe, "2y")
        try:
            df = await asyncio.to_thread(lambda: yf.Ticker(ticker).history(period=period, interval=interval))
        except Exception as exc:
            raise ProviderError(str(exc)) from exc

        if df.empty:
            raise ProviderDataError(f"No OHLCV data returned for {ticker!r}")

        if isinstance(df.columns, tuple):
            df.columns = [c[1] if isinstance(c, tuple) else c for c in df.columns]

        result: list[OHLCVBar] = []
        for index, row in df.iterrows():
            ts = index.isoformat() if hasattr(index, "isoformat") else str(index)
            result.append(
                OHLCVBar(
                    timestamp=ts,
                    open=round(float(row["Open"]), 2),
                    high=round(float(row["High"]), 2),
                    low=round(float(row["Low"]), 2),
                    close=round(float(row["Close"]), 2),
                    volume=int(row["Volume"]),
                )
            )

        return result[-bars:]

    def status(self) -> dict[str, object]:
        return {
            "name": "market_data",
            "mode": "live",
            "configured": True,
            "message": "Fetching live OHLCV from Yahoo Finance.",
        }
