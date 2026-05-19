from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

AssetType = Literal["stock", "etf"]
Timeframe = Literal["15m", "1h", "4h", "1D", "1W"]
Horizon = Literal["short", "swing", "long"]
Sentiment = Literal["positive", "neutral", "negative", "mixed"]
CatalystType = Literal[
    "earnings",
    "guidance",
    "analyst_rating",
    "macro",
    "legal_regulatory",
    "product",
    "management",
    "m_and_a",
    "insider",
    "sector",
    "other",
]
ScreenshotSignalAction = Literal["buy", "sell", "neutral", "insufficient"]
ScreenshotCandleDirection = Literal["bullish", "bearish", "doji"]


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    asset_type: AssetType = "stock"
    timeframe: Timeframe = "1D"
    horizon: Horizon = "swing"
    include_news: bool = True
    include_fundamentals: bool = True

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


class ScreenshotParseRequest(BaseModel):
    image_base64: str | None = None
    filename: str | None = None


class ScreenshotExtractionSummary(BaseModel):
    candle_count: int
    calibration_confidence: str
    warnings: list[str]


class ScreenshotCandle(BaseModel):
    index: int
    timestamp_label: str | None = None
    open: float
    high: float
    low: float
    close: float
    direction: ScreenshotCandleDirection
    confidence: str


class ScreenshotSignal(BaseModel):
    action: ScreenshotSignalAction
    score: int
    confidence: str
    reasons: list[str]
    risk_warnings: list[str]


class ScreenshotParseResponse(BaseModel):
    detected_ticker: str | None = None
    detected_timeframe: str | None = None
    confidence: str
    needs_confirmation: bool
    notes: str
    extraction: ScreenshotExtractionSummary
    candles: list[ScreenshotCandle]
    signal: ScreenshotSignal


class OHLCVBar(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class PriceSummary(BaseModel):
    last_close: float
    change_pct: float
    volume: int


class IndicatorSummary(BaseModel):
    sma20: float | None = None
    sma50: float | None = None
    sma200: float | None = None
    ema12: float | None = None
    ema26: float | None = None
    rsi14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    bollinger_upper: float | None = None
    bollinger_middle: float | None = None
    bollinger_lower: float | None = None
    atr14: float | None = None
    volume_ratio: float | None = None


class SupportResistance(BaseModel):
    support: list[float]
    resistance: list[float]


class TechnicalAnalysis(BaseModel):
    setup: str
    score: int
    confidence: str
    indicators: IndicatorSummary
    support_resistance: SupportResistance
    evidence: list[str]
    risks: list[str]
    trend_score: int | None = None
    momentum_score: int | None = None
    structure_score: int | None = None
    volume_score: int | None = None
    volatility_score: int | None = None


class NewsItem(BaseModel):
    title: str
    source: str
    published_at: str
    url: str | None = None
    sentiment: Sentiment
    catalyst_type: CatalystType
    summary: str


class NewsSummary(BaseModel):
    sentiment: Sentiment
    score: int
    items: list[NewsItem]
    summary: str


class FundamentalMetrics(BaseModel):
    revenue_growth: float | None = None
    earnings_growth: float | None = None
    free_cash_flow: float | None = None
    debt_to_equity: float | None = None
    pe_ratio: float | None = None
    forward_pe: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None


class FundamentalsSummary(BaseModel):
    quality: Literal["strong", "average", "weak", "unavailable"]
    score: int
    metrics: FundamentalMetrics
    summary: str
    growth_score: int | None = None
    profitability_score: int | None = None
    balance_sheet_score: int | None = None
    valuation_score: int | None = None
    cash_flow_score: int | None = None


class DataQualitySummary(BaseModel):
    score: int
    status: Literal["usable", "limited", "insufficient"]
    bars_count: int
    latest_timestamp: str | None = None
    warnings: list[str]


class RiskSummary(BaseModel):
    score: int
    level: Literal["low", "moderate", "elevated", "high"]
    atr_pct: float | None = None
    realized_volatility_20d: float | None = None
    realized_volatility_60d: float | None = None
    max_drawdown_60d: float | None = None
    average_dollar_volume_20d: float | None = None
    warnings: list[str]


class MarketContextSummary(BaseModel):
    score: int
    benchmark: str
    relative_strength_20d: float | None = None
    relative_strength_60d: float | None = None
    summary: str


class OverallSummary(BaseModel):
    label: str
    score: int
    confidence: str
    conclusion: str


class AnalyzeResponse(BaseModel):
    ticker: str
    asset_type: AssetType
    timeframe: Timeframe
    horizon: Horizon
    generated_at: str
    data_mode: Literal["live", "unavailable", "mixed"]
    price_summary: PriceSummary
    data_quality: DataQualitySummary
    technical: TechnicalAnalysis
    risk: RiskSummary
    news: NewsSummary
    fundamentals: FundamentalsSummary
    market_context: MarketContextSummary
    overall: OverallSummary
