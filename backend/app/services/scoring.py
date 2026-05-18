from __future__ import annotations

from app.models import IndicatorSummary, NewsSummary, TechnicalAnalysis


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
    return evidence or ["Indicator evidence is limited because available data is incomplete."]


def technical_risks(indicators: IndicatorSummary, last_close: float) -> list[str]:
    risks = ["Past performance does not guarantee future results."]
    if indicators.sma50 is not None:
        risks.append("A close below the 50-period moving average would weaken the current technical setup." if last_close >= indicators.sma50 else "Price is below the 50-period moving average, which may signal trend weakness.")
    if indicators.atr14 is not None:
        risks.append("ATR indicates volatility can materially change the setup before confirmation.")
    if indicators.volume_ratio is not None and indicators.volume_ratio < 1.0:
        risks.append("Volume confirmation is limited compared with the recent average.")
    return risks


def overall_score(technical: TechnicalAnalysis, news: NewsSummary, fundamental_score: int) -> int:
    return clamp(round((technical.score * 0.60) + ((news.score + 50) * 0.15) + (fundamental_score * 0.25)))
