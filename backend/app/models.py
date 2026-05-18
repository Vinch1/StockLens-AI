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


class OverallSummary(BaseModel):
    label: str
    score: int
    confidence: str
    educational_conclusion: str


class AnalyzeResponse(BaseModel):
    ticker: str
    asset_type: AssetType
    timeframe: Timeframe
    horizon: Horizon
    generated_at: str
    data_mode: Literal["mock", "live"]
    price_summary: PriceSummary
    technical: TechnicalAnalysis
    news: NewsSummary
    fundamentals: FundamentalsSummary
    overall: OverallSummary
    disclaimer: str
