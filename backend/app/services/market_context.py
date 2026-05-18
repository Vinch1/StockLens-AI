from __future__ import annotations

from app.models import MarketContextSummary, OHLCVBar
from app.services.scoring import clamp


def _round(value: float | None, places: int = 4) -> float | None:
    return None if value is None else round(value, places)


def _period_return(bars: list[OHLCVBar], period: int) -> float | None:
    if len(bars) <= period:
        return None
    start = bars[-(period + 1)].close
    end = bars[-1].close
    if not start:
        return None
    return ((end / start) - 1) * 100


def market_context_from_bars(
    stock_bars: list[OHLCVBar],
    benchmark_bars: list[OHLCVBar] | None = None,
    benchmark: str = "SPY",
) -> MarketContextSummary:
    stock_return_20d = _period_return(stock_bars, 20)
    stock_return_60d = _period_return(stock_bars, 60)
    benchmark_return_20d = _period_return(benchmark_bars or [], 20)
    benchmark_return_60d = _period_return(benchmark_bars or [], 60)

    relative_strength_20d = (
        stock_return_20d - benchmark_return_20d
        if stock_return_20d is not None and benchmark_return_20d is not None
        else None
    )
    relative_strength_60d = (
        stock_return_60d - benchmark_return_60d
        if stock_return_60d is not None and benchmark_return_60d is not None
        else None
    )

    score = 50
    if relative_strength_20d is not None:
        if relative_strength_20d > 5:
            score += 15
        elif relative_strength_20d > 0:
            score += 8
        elif relative_strength_20d < -5:
            score -= 15
        elif relative_strength_20d < 0:
            score -= 8

    if relative_strength_60d is not None:
        if relative_strength_60d > 8:
            score += 20
        elif relative_strength_60d > 0:
            score += 10
        elif relative_strength_60d < -8:
            score -= 20
        elif relative_strength_60d < 0:
            score -= 10

    score = clamp(score)

    if relative_strength_20d is None and relative_strength_60d is None:
        summary = "Benchmark context is unavailable; market-context confidence is limited."
    elif score >= 65:
        summary = f"Relative strength versus {benchmark} is constructive across available windows."
    elif score <= 35:
        summary = f"Relative strength versus {benchmark} is weak across available windows."
    else:
        summary = f"Relative strength versus {benchmark} is mixed."

    return MarketContextSummary(
        score=score,
        benchmark=benchmark,
        relative_strength_20d=_round(relative_strength_20d),
        relative_strength_60d=_round(relative_strength_60d),
        summary=summary,
    )
