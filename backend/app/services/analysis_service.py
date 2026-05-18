from __future__ import annotations

from datetime import UTC, datetime

from app.models import AnalyzeRequest, AnalyzeResponse, PriceSummary, TechnicalAnalysis
from app.providers.mock import fundamentals_provider, market_provider, news_provider
from app.services.compliance import DISCLAIMER
from app.services.explanation import educational_conclusion
from app.services.indicators import compute_indicators, support_resistance
from app.services.scoring import confidence, overall_score, setup_label, technical_evidence, technical_risks, technical_score


def analyze_ticker(request: AnalyzeRequest) -> AnalyzeResponse:
    bars = market_provider.get_ohlcv(request.ticker, request.timeframe)
    if len(bars) < 2:
        raise ValueError("At least two OHLCV bars are required for analysis.")
    indicators = compute_indicators(bars)
    last = bars[-1]
    previous = bars[-2]
    change_pct = ((last.close - previous.close) / previous.close) * 100 if previous.close else 0
    score = technical_score(indicators, last.close, previous.close, indicators.volume_ratio)
    technical = TechnicalAnalysis(
        setup=setup_label(score, indicators),
        score=score,
        confidence=confidence(market_provider.mode, len(bars), score, indicators),
        indicators=indicators,
        support_resistance=support_resistance(bars),
        evidence=technical_evidence(indicators, last.close),
        risks=technical_risks(indicators, last.close),
    )
    news = news_provider.get_news(request.ticker) if request.include_news else news_provider.get_news(request.ticker).model_copy(update={"items": [], "score": 0, "sentiment": "neutral", "summary": "News analysis was not requested."})
    fundamentals = fundamentals_provider.get_fundamentals(request.ticker) if request.include_fundamentals else fundamentals_provider.get_fundamentals(request.ticker).model_copy(update={"summary": "Fundamental analysis was not requested."})
    combined_score = overall_score(technical, news, fundamentals.score)
    combined_confidence = "low" if market_provider.mode == "mock" else technical.confidence
    conclusion = educational_conclusion(technical, combined_score, combined_confidence)
    label = (
        "watchlist_research_candidate" if combined_score >= 70 else
        "mixed_research_candidate" if combined_score >= 55 else
        "needs_more_confirmation" if combined_score >= 40 else
        "high_risk_setup"
    )
    return AnalyzeResponse(
        ticker=request.ticker,
        asset_type=request.asset_type,
        timeframe=request.timeframe,
        horizon=request.horizon,
        generated_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
        data_mode=market_provider.mode,
        price_summary=PriceSummary(last_close=last.close, change_pct=round(change_pct, 2), volume=last.volume),
        technical=technical,
        news=news,
        fundamentals=fundamentals,
        overall={"label": label, "score": combined_score, "confidence": combined_confidence, "educational_conclusion": conclusion},
        disclaimer=DISCLAIMER,
    )
