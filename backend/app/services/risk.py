from __future__ import annotations

import math
from statistics import mean, stdev

from app.models import IndicatorSummary, OHLCVBar, RiskSummary
from app.services.scoring import clamp


def _round(value: float | None, places: int = 4) -> float | None:
    return None if value is None else round(value, places)


def _returns(closes: list[float]) -> list[float]:
    values: list[float] = []
    for current, previous in zip(closes[1:], closes[:-1]):
        if previous:
            values.append((current / previous) - 1)
    return values


def _annualized_volatility(closes: list[float], period: int) -> float | None:
    if len(closes) <= period:
        return None
    recent_returns = _returns(closes[-(period + 1):])
    if len(recent_returns) < 2:
        return None
    return stdev(recent_returns) * math.sqrt(252) * 100


def _max_drawdown(closes: list[float], period: int = 60) -> float | None:
    if len(closes) < 2:
        return None
    window = closes[-period:]
    peak = window[0]
    worst = 0.0
    for close in window:
        peak = max(peak, close)
        if peak:
            worst = min(worst, (close / peak) - 1)
    return worst * 100


def _average_dollar_volume(bars: list[OHLCVBar], period: int = 20) -> float | None:
    if len(bars) < period:
        return None
    return mean(bar.close * bar.volume for bar in bars[-period:])


def assess_risk(bars: list[OHLCVBar], indicators: IndicatorSummary) -> RiskSummary:
    closes = [bar.close for bar in bars]
    last_close = closes[-1] if closes else 0
    atr_pct = (indicators.atr14 / last_close) * 100 if indicators.atr14 and last_close else None
    realized_20d = _annualized_volatility(closes, 20)
    realized_60d = _annualized_volatility(closes, 60)
    max_drawdown_60d = _max_drawdown(closes, 60)
    average_dollar_volume_20d = _average_dollar_volume(bars, 20)

    score = 100
    warnings: list[str] = []

    if atr_pct is not None:
        if atr_pct > 8:
            score -= 30
            warnings.append("ATR is very high relative to price, so near-term volatility risk is high.")
        elif atr_pct > 5:
            score -= 20
            warnings.append("ATR is elevated relative to price.")
        elif atr_pct > 3:
            score -= 10
            warnings.append("ATR shows moderate volatility.")

    if realized_20d is not None:
        if realized_20d > 80:
            score -= 20
            warnings.append("20-day realized volatility is very elevated.")
        elif realized_20d > 45:
            score -= 10
            warnings.append("20-day realized volatility is elevated.")

    if max_drawdown_60d is not None:
        if max_drawdown_60d < -35:
            score -= 20
            warnings.append("Recent drawdown is severe.")
        elif max_drawdown_60d < -20:
            score -= 10
            warnings.append("Recent drawdown is material.")

    if average_dollar_volume_20d is not None and average_dollar_volume_20d < 10_000_000:
        score -= 10
        warnings.append("Average dollar volume is relatively low, which can increase liquidity risk.")

    score = clamp(score)
    if score >= 80:
        level = "low"
    elif score >= 60:
        level = "moderate"
    elif score >= 40:
        level = "elevated"
    else:
        level = "high"

    return RiskSummary(
        score=score,
        level=level,
        atr_pct=_round(atr_pct),
        realized_volatility_20d=_round(realized_20d),
        realized_volatility_60d=_round(realized_60d),
        max_drawdown_60d=_round(max_drawdown_60d),
        average_dollar_volume_20d=_round(average_dollar_volume_20d, 2),
        warnings=warnings,
    )
