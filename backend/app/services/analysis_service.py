from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime

from loguru import logger

from app.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    FundamentalMetrics,
    FundamentalsSummary,
    NewsSummary,
    PriceSummary,
    TechnicalAnalysis,
)
from app.providers.protocols import ExplanationProvider, FundamentalsProvider, MarketDataProvider, NewsProvider
from app.services.data_quality import assess_data_quality
from app.services.explanation import get_report_conclusion
from app.services.indicators import compute_indicators, support_resistance
from app.services.market_context import market_context_from_bars
from app.services.risk import assess_risk
from app.services.scoring import (
    SCORE_MODEL_VERSION,
    confidence_v2,
    overall_score_breakdown,
    setup_label,
    technical_evidence,
    technical_risks,
    technical_score_from_subscores,
    technical_subscores,
)


def _disabled_news() -> NewsSummary:
    return NewsSummary(sentiment="neutral", score=0, items=[], summary="News analysis was not requested.")


def _unavailable_news(reason: str) -> NewsSummary:
    return NewsSummary(
        sentiment="neutral",
        score=0,
        items=[],
        summary=f"News analysis is unavailable: {reason}",
    )


def _disabled_fundamentals() -> FundamentalsSummary:
    return FundamentalsSummary(
        quality="unavailable",
        score=50,
        metrics=FundamentalMetrics(),
        summary="Fundamental analysis was not requested.",
    )


def _unavailable_fundamentals(reason: str) -> FundamentalsSummary:
    return FundamentalsSummary(
        quality="unavailable",
        score=50,
        metrics=FundamentalMetrics(),
        summary=f"Fundamental analysis is unavailable: {reason}",
    )


def _news_available(requested: bool, news: NewsSummary) -> bool:
    return requested and not news.summary.startswith("News analysis is unavailable")


def _response_data_mode(*modes: str) -> str:
    clean_modes = {mode for mode in modes if mode}
    active_modes = {mode for mode in clean_modes if mode != "unavailable"}
    if not active_modes:
        return "unavailable"
    if "unavailable" in clean_modes:
        return "mixed"
    if len(active_modes) == 1:
        return active_modes.pop()
    return "mixed"


async def analyze_ticker(
    request: AnalyzeRequest,
    market_provider: MarketDataProvider,
    news_provider: NewsProvider,
    fundamentals_provider: FundamentalsProvider,
    explanation_provider: ExplanationProvider | None = None,
) -> AnalyzeResponse:
    bars_coro = market_provider.get_ohlcv(request.ticker, request.timeframe)
    benchmark_coro = market_provider.get_ohlcv("SPY", request.timeframe)

    bars_result, benchmark_result = await asyncio.gather(bars_coro, benchmark_coro, return_exceptions=True)
    if isinstance(bars_result, Exception):
        raise bars_result
    bars = bars_result
    if isinstance(benchmark_result, Exception):
        benchmark_bars = None
    else:
        benchmark_bars = benchmark_result

    if request.include_news:
        try:
            news = await news_provider.get_news(request.ticker)
        except Exception as exc:
            news = _unavailable_news(str(exc))
        _log_collected_news(request.ticker, news)
    else:
        news = _disabled_news()

    if request.include_fundamentals:
        try:
            fundamentals = await fundamentals_provider.get_fundamentals(request.ticker)
        except Exception as exc:
            fundamentals = _unavailable_fundamentals(str(exc))
    else:
        fundamentals = _disabled_fundamentals()

    if len(bars) < 2:
        raise ValueError("At least two OHLCV bars are required for analysis.")
    indicators = compute_indicators(bars)
    last = bars[-1]
    previous = bars[-2]
    change_pct = ((last.close - previous.close) / previous.close) * 100 if previous.close else 0
    levels = support_resistance(bars)
    subscores = technical_subscores(indicators, last.close, previous.close, levels)
    score = technical_score_from_subscores(subscores)
    data_quality = assess_data_quality(bars)
    risk = assess_risk(bars, indicators)
    market_context = market_context_from_bars(bars, benchmark_bars, benchmark="SPY")
    technical = TechnicalAnalysis(
        setup=setup_label(score, indicators),
        score=score,
        confidence="low",
        indicators=indicators,
        support_resistance=levels,
        evidence=technical_evidence(indicators, last.close),
        risks=[*technical_risks(indicators, last.close), *risk.warnings],
        **subscores,
    )
    fundamentals_available = request.include_fundamentals and fundamentals.quality != "unavailable"
    score_breakdown = overall_score_breakdown(
        technical=technical,
        news=news,
        fundamental_score=fundamentals.score,
        risk=risk,
        market_context=market_context,
        horizon=request.horizon,
        news_available=_news_available(request.include_news, news),
        fundamentals_available=fundamentals_available,
    )
    combined_score = score_breakdown.risk_adjusted_score
    combined_confidence = confidence_v2(
        data_quality=data_quality,
        technical=technical,
        risk=risk,
        market_context=market_context,
        horizon=request.horizon,
        fundamentals_available=fundamentals_available,
        score_breakdown=score_breakdown,
    )
    technical.confidence = combined_confidence
    conclusion = await get_report_conclusion(
        technical, combined_score, combined_confidence,
        explanation_provider=explanation_provider,
        news_summary=news.summary,
        fundamentals_summary=fundamentals.summary,
    )
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
        data_mode=_response_data_mode(
            market_provider.mode,
            news_provider.mode if request.include_news else "",
            fundamentals_provider.mode if request.include_fundamentals else "",
        ),
        price_summary=PriceSummary(last_close=last.close, change_pct=round(change_pct, 2), volume=last.volume),
        data_quality=data_quality,
        technical=technical,
        risk=risk,
        news=news,
        fundamentals=fundamentals,
        market_context=market_context,
        overall={
            "label": label,
            "score": combined_score,
            "confidence": combined_confidence,
            "conclusion": conclusion,
            "score_model_version": SCORE_MODEL_VERSION,
            "score_breakdown": score_breakdown,
        },
    )


def _log_collected_news(ticker: str, news: NewsSummary) -> None:
    payload = {
        "ticker": ticker,
        "sentiment": news.sentiment,
        "score": news.score,
        "summary": news.summary,
        "item_count": len(news.items),
        "items": [item.model_dump(mode="json") for item in news.items],
    }
    level = "WARNING" if news.summary.startswith("News analysis is unavailable") else "INFO"
    logger.log(level, "Collected news {}", json.dumps(payload, ensure_ascii=False))
