from __future__ import annotations

from app.models import (
    DataQualitySummary,
    IndicatorSummary,
    MarketContextSummary,
    NewsSummary,
    RiskSummary,
    SupportResistance,
    TechnicalAnalysis,
)


def clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


def setup_label(score: int, indicators: IndicatorSummary) -> str:
    if indicators.atr14 and indicators.bollinger_middle and indicators.atr14 / indicators.bollinger_middle > 0.08:
        return "high_risk_mixed"
    if score >= 75:
        return "bullish"
    if score >= 60:
        return "neutral_to_bullish"
    if score >= 45:
        return "neutral"
    if score >= 30:
        return "neutral_to_bearish"
    return "bearish"


def confidence(bars_count: int, score: int, indicators: IndicatorSummary) -> str:
    if bars_count < 200:
        return "low"
    conflict_count = 0
    if indicators.macd is not None and indicators.macd_signal is not None:
        if (score >= 60 and indicators.macd < indicators.macd_signal) or (score <= 40 and indicators.macd > indicators.macd_signal):
            conflict_count += 1
    if indicators.rsi14 is not None and ((score >= 60 and indicators.rsi14 > 75) or (score <= 40 and indicators.rsi14 < 30)):
        conflict_count += 1
    if conflict_count:
        return "medium"
    return "high" if score >= 75 or score <= 25 else "medium"


def technical_score(indicators: IndicatorSummary, last_close: float, previous_close: float, last_volume_ratio: float | None) -> int:
    score = 50
    if indicators.sma20 is not None:
        score += 8 if last_close > indicators.sma20 else -8
    if indicators.sma50 is not None:
        score += 8 if last_close > indicators.sma50 else -8
    if indicators.sma200 is not None:
        score += 10 if last_close > indicators.sma200 else -10
    if indicators.sma20 is not None and indicators.sma50 is not None:
        score += 8 if indicators.sma20 > indicators.sma50 else -8
    if indicators.sma50 is not None and indicators.sma200 is not None and indicators.sma50 > indicators.sma200:
        score += 8
    if indicators.macd is not None and indicators.macd_signal is not None:
        score += 8 if indicators.macd > indicators.macd_signal else -8
    if indicators.macd_histogram is not None and indicators.macd_histogram > 0:
        score += 5
    if indicators.rsi14 is not None:
        if 45 <= indicators.rsi14 <= 65:
            score += 5
        if indicators.rsi14 > 75:
            score -= 8
        if indicators.rsi14 < 30:
            score -= 8
    if last_volume_ratio is not None:
        if last_volume_ratio > 1.2 and last_close > previous_close:
            score += 5
        if last_volume_ratio > 1.5 and last_close < previous_close:
            score -= 8
    return clamp(score)


def _score_from_adjustments(adjustments: list[int]) -> int:
    return clamp(50 + sum(adjustments))


def technical_subscores(
    indicators: IndicatorSummary,
    last_close: float,
    previous_close: float,
    support_resistance: SupportResistance,
) -> dict[str, int]:
    trend_adjustments: list[int] = []
    if indicators.sma20 is not None:
        trend_adjustments.append(10 if last_close > indicators.sma20 else -10)
    if indicators.sma50 is not None:
        trend_adjustments.append(10 if last_close > indicators.sma50 else -10)
    if indicators.sma200 is not None:
        trend_adjustments.append(15 if last_close > indicators.sma200 else -15)
    if indicators.sma20 is not None and indicators.sma50 is not None:
        trend_adjustments.append(10 if indicators.sma20 > indicators.sma50 else -10)
    if indicators.sma50 is not None and indicators.sma200 is not None:
        trend_adjustments.append(10 if indicators.sma50 > indicators.sma200 else -10)

    momentum_adjustments: list[int] = []
    if indicators.macd is not None and indicators.macd_signal is not None:
        momentum_adjustments.append(12 if indicators.macd > indicators.macd_signal else -12)
    if indicators.macd_histogram is not None:
        momentum_adjustments.append(8 if indicators.macd_histogram > 0 else -8)
    if indicators.rsi14 is not None:
        if 45 <= indicators.rsi14 <= 65:
            momentum_adjustments.append(10)
        elif 35 <= indicators.rsi14 < 45 or 65 < indicators.rsi14 <= 75:
            momentum_adjustments.append(2)
        elif indicators.rsi14 > 80 or indicators.rsi14 < 25:
            momentum_adjustments.append(-12)
        else:
            momentum_adjustments.append(-6)

    structure_adjustments: list[int] = []
    if support_resistance.support:
        nearest_support = max(support_resistance.support)
        if last_close >= nearest_support:
            structure_adjustments.append(8)
            if indicators.atr14 and indicators.atr14 > 0:
                distance = (last_close - nearest_support) / indicators.atr14
                if distance <= 2:
                    structure_adjustments.append(7)
    if support_resistance.resistance:
        nearest_resistance = min(support_resistance.resistance)
        if last_close > nearest_resistance:
            structure_adjustments.append(10)
        elif indicators.atr14 and indicators.atr14 > 0:
            distance = (nearest_resistance - last_close) / indicators.atr14
            if distance < 1:
                structure_adjustments.append(-8)

    volume_adjustments: list[int] = []
    if indicators.volume_ratio is not None:
        if indicators.volume_ratio > 1.5 and last_close > previous_close:
            volume_adjustments.append(18)
        elif indicators.volume_ratio > 1.2 and last_close > previous_close:
            volume_adjustments.append(10)
        elif indicators.volume_ratio > 1.5 and last_close < previous_close:
            volume_adjustments.append(-18)
        elif indicators.volume_ratio < 0.8:
            volume_adjustments.append(-6)

    volatility_adjustments: list[int] = []
    if indicators.atr14 is not None and last_close:
        atr_pct = (indicators.atr14 / last_close) * 100
        if atr_pct <= 2:
            volatility_adjustments.append(12)
        elif atr_pct <= 4:
            volatility_adjustments.append(5)
        elif atr_pct <= 7:
            volatility_adjustments.append(-8)
        else:
            volatility_adjustments.append(-20)
    if indicators.bollinger_upper is not None and indicators.bollinger_lower is not None and indicators.bollinger_middle:
        band_width = (indicators.bollinger_upper - indicators.bollinger_lower) / indicators.bollinger_middle
        if band_width > 0.18:
            volatility_adjustments.append(-8)
        elif band_width < 0.06:
            volatility_adjustments.append(5)

    return {
        "trend_score": _score_from_adjustments(trend_adjustments),
        "momentum_score": _score_from_adjustments(momentum_adjustments),
        "structure_score": _score_from_adjustments(structure_adjustments),
        "volume_score": _score_from_adjustments(volume_adjustments),
        "volatility_score": _score_from_adjustments(volatility_adjustments),
    }


def technical_score_from_subscores(subscores: dict[str, int]) -> int:
    return clamp(round(
        (subscores["trend_score"] * 0.30)
        + (subscores["momentum_score"] * 0.20)
        + (subscores["structure_score"] * 0.20)
        + (subscores["volume_score"] * 0.15)
        + (subscores["volatility_score"] * 0.15)
    ))


def technical_evidence(indicators: IndicatorSummary, last_close: float) -> list[str]:
    evidence: list[str] = []
    if indicators.sma20 is not None and indicators.sma50 is not None:
        relation = "above" if last_close > indicators.sma20 and last_close > indicators.sma50 else "not consistently above"
        evidence.append(f"Price is {relation} the 20-period and 50-period moving averages.")
    if indicators.rsi14 is not None:
        if 45 <= indicators.rsi14 <= 65:
            evidence.append("RSI is moderate, which avoids an extreme overbought or oversold reading.")
        elif indicators.rsi14 > 75:
            evidence.append("RSI is elevated, so momentum may be stretched in the short term.")
        elif indicators.rsi14 < 30:
            evidence.append("RSI is depressed, which can indicate weak momentum or an oversold condition.")
    if indicators.macd is not None and indicators.macd_signal is not None:
        evidence.append("MACD is above its signal line." if indicators.macd > indicators.macd_signal else "MACD is below its signal line.")
    if indicators.volume_ratio is not None:
        evidence.append(f"Latest volume is {indicators.volume_ratio:.2f}x the recent average volume.")
    if indicators.atr14 is not None and last_close:
        evidence.append(f"ATR is {((indicators.atr14 / last_close) * 100):.2f}% of price, which helps frame volatility risk.")
    return evidence or ["Indicator evidence is limited because available data is incomplete."]


def technical_risks(indicators: IndicatorSummary, last_close: float) -> list[str]:
    risks = ["Past performance does not guarantee future results."]
    if indicators.sma50 is not None:
        risks.append("A close below the 50-period moving average would weaken the current technical setup." if last_close >= indicators.sma50 else "Price is below the 50-period moving average, which may signal trend weakness.")
    if indicators.atr14 is not None:
        risks.append("ATR indicates volatility can materially change the setup before confirmation.")
    if indicators.volume_ratio is not None and indicators.volume_ratio < 1.0:
        risks.append("Volume confirmation is limited compared with the recent average.")
    if indicators.rsi14 is not None and indicators.rsi14 > 75:
        risks.append("RSI is elevated, so the setup may be technically extended.")
    return risks


def overall_score(technical: TechnicalAnalysis, news: NewsSummary, fundamental_score: int) -> int:
    return clamp(round((technical.score * 0.60) + ((news.score + 50) * 0.15) + (fundamental_score * 0.25)))


def horizon_weights(horizon: str) -> dict[str, float]:
    if horizon == "short":
        return {
            "technical": 0.55,
            "fundamentals": 0.00,
            "risk": 0.20,
            "news": 0.15,
            "market_context": 0.10,
        }
    if horizon == "long":
        return {
            "technical": 0.20,
            "fundamentals": 0.45,
            "risk": 0.15,
            "news": 0.10,
            "market_context": 0.10,
        }
    return {
        "technical": 0.40,
        "fundamentals": 0.20,
        "risk": 0.15,
        "news": 0.15,
        "market_context": 0.10,
    }


def overall_score_v2(
    technical: TechnicalAnalysis,
    news: NewsSummary,
    fundamental_score: int,
    risk: RiskSummary,
    market_context: MarketContextSummary,
    horizon: str,
) -> int:
    weights = horizon_weights(horizon)
    adjusted_news_score = news.score + 50
    return clamp(round(
        (technical.score * weights["technical"])
        + (fundamental_score * weights["fundamentals"])
        + (risk.score * weights["risk"])
        + (adjusted_news_score * weights["news"])
        + (market_context.score * weights["market_context"])
    ))


def confidence_v2(
    data_quality: DataQualitySummary,
    technical: TechnicalAnalysis,
    risk: RiskSummary,
    market_context: MarketContextSummary,
    horizon: str,
    fundamentals_available: bool,
) -> str:
    score = data_quality.score

    if data_quality.bars_count < 200:
        score -= 10
    if risk.level in {"elevated", "high"}:
        score -= 10 if risk.level == "elevated" else 20
    if horizon == "long" and not fundamentals_available:
        score -= 15
    if market_context.relative_strength_20d is None and market_context.relative_strength_60d is None:
        score -= 10

    subscores = [
        technical.trend_score,
        technical.momentum_score,
        technical.structure_score,
        technical.volume_score,
        technical.volatility_score,
    ]
    populated = [value for value in subscores if value is not None]
    if populated and max(populated) - min(populated) > 45:
        score -= 12

    if score >= 80:
        return "high"
    if score >= 55:
        return "medium"
    return "low"
