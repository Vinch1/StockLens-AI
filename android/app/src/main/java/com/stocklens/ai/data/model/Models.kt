package com.stocklens.ai.data.model

import com.google.gson.annotations.SerializedName

data class AnalyzeRequest(
    val ticker: String,
    @SerializedName("asset_type") val assetType: String = "stock",
    val timeframe: String = "1D",
    val horizon: String = "swing",
    @SerializedName("include_news") val includeNews: Boolean = true,
    @SerializedName("include_fundamentals") val includeFundamentals: Boolean = true
)

data class ScreenshotParseRequest(
    @SerializedName("image_base64") val imageBase64: String? = null,
    val filename: String? = null
)

data class ScreenshotExtractionSummary(
    @SerializedName("candle_count") val candleCount: Int,
    @SerializedName("calibration_confidence") val calibrationConfidence: String,
    val warnings: List<String> = emptyList()
)

data class ScreenshotCandle(
    val index: Int,
    @SerializedName("timestamp_label") val timestampLabel: String? = null,
    val open: Double,
    val high: Double,
    val low: Double,
    val close: Double,
    val direction: String,
    val confidence: String
)

data class ScreenshotSignal(
    val action: String,
    val score: Int,
    val confidence: String,
    val reasons: List<String> = emptyList(),
    @SerializedName("risk_warnings") val riskWarnings: List<String> = emptyList()
)

data class ScreenshotParseResponse(
    @SerializedName("detected_ticker") val detectedTicker: String? = null,
    @SerializedName("detected_timeframe") val detectedTimeframe: String? = null,
    val confidence: String,
    @SerializedName("needs_confirmation") val needsConfirmation: Boolean,
    val notes: String,
    val extraction: ScreenshotExtractionSummary,
    val candles: List<ScreenshotCandle> = emptyList(),
    val signal: ScreenshotSignal
)

data class PriceSummary(
    @SerializedName("last_close") val lastClose: Double,
    @SerializedName("change_pct") val changePct: Double,
    val volume: Long
)

data class IndicatorSummary(
    val sma20: Double? = null,
    val sma50: Double? = null,
    val sma200: Double? = null,
    val ema12: Double? = null,
    val ema26: Double? = null,
    val rsi14: Double? = null,
    val macd: Double? = null,
    @SerializedName("macd_signal") val macdSignal: Double? = null,
    @SerializedName("macd_histogram") val macdHistogram: Double? = null,
    @SerializedName("bollinger_upper") val bollingerUpper: Double? = null,
    @SerializedName("bollinger_middle") val bollingerMiddle: Double? = null,
    @SerializedName("bollinger_lower") val bollingerLower: Double? = null,
    val atr14: Double? = null,
    @SerializedName("volume_ratio") val volumeRatio: Double? = null
)

data class SupportResistance(
    val support: List<Double> = emptyList(),
    val resistance: List<Double> = emptyList()
)

data class TechnicalAnalysis(
    val setup: String,
    val score: Int,
    val confidence: String,
    val indicators: IndicatorSummary,
    @SerializedName("support_resistance") val supportResistance: SupportResistance,
    val evidence: List<String>,
    val risks: List<String>,
    @SerializedName("trend_score") val trendScore: Int? = null,
    @SerializedName("momentum_score") val momentumScore: Int? = null,
    @SerializedName("structure_score") val structureScore: Int? = null,
    @SerializedName("volume_score") val volumeScore: Int? = null,
    @SerializedName("volatility_score") val volatilityScore: Int? = null
)

data class NewsItem(
    val title: String,
    val source: String,
    @SerializedName("published_at") val publishedAt: String,
    val url: String? = null,
    val sentiment: String,
    @SerializedName("catalyst_type") val catalystType: String,
    val summary: String
)

data class NewsSummary(
    val sentiment: String,
    val score: Int,
    val items: List<NewsItem>,
    val summary: String
)

data class FundamentalMetrics(
    @SerializedName("revenue_growth") val revenueGrowth: Double? = null,
    @SerializedName("earnings_growth") val earningsGrowth: Double? = null,
    @SerializedName("free_cash_flow") val freeCashFlow: Double? = null,
    @SerializedName("debt_to_equity") val debtToEquity: Double? = null,
    @SerializedName("pe_ratio") val peRatio: Double? = null,
    @SerializedName("forward_pe") val forwardPe: Double? = null,
    @SerializedName("gross_margin") val grossMargin: Double? = null,
    @SerializedName("operating_margin") val operatingMargin: Double? = null
)

data class FundamentalsSummary(
    val quality: String,
    val score: Int,
    val metrics: FundamentalMetrics,
    val summary: String,
    @SerializedName("growth_score") val growthScore: Int? = null,
    @SerializedName("profitability_score") val profitabilityScore: Int? = null,
    @SerializedName("balance_sheet_score") val balanceSheetScore: Int? = null,
    @SerializedName("valuation_score") val valuationScore: Int? = null,
    @SerializedName("cash_flow_score") val cashFlowScore: Int? = null
)

data class DataQualitySummary(
    val score: Int,
    val status: String,
    @SerializedName("bars_count") val barsCount: Int,
    @SerializedName("latest_timestamp") val latestTimestamp: String? = null,
    val warnings: List<String> = emptyList()
)

data class RiskSummary(
    val score: Int,
    val level: String,
    @SerializedName("atr_pct") val atrPct: Double? = null,
    @SerializedName("realized_volatility_20d") val realizedVolatility20d: Double? = null,
    @SerializedName("realized_volatility_60d") val realizedVolatility60d: Double? = null,
    @SerializedName("max_drawdown_60d") val maxDrawdown60d: Double? = null,
    @SerializedName("average_dollar_volume_20d") val averageDollarVolume20d: Double? = null,
    val warnings: List<String> = emptyList()
)

data class MarketContextSummary(
    val score: Int,
    val benchmark: String,
    @SerializedName("relative_strength_20d") val relativeStrength20d: Double? = null,
    @SerializedName("relative_strength_60d") val relativeStrength60d: Double? = null,
    val summary: String
)

data class OverallSummary(
    val label: String,
    val score: Int,
    val confidence: String,
    val conclusion: String
)

data class AnalyzeResponse(
    val ticker: String,
    @SerializedName("asset_type") val assetType: String,
    val timeframe: String,
    val horizon: String,
    @SerializedName("generated_at") val generatedAt: String,
    @SerializedName("data_mode") val dataMode: String,
    @SerializedName("price_summary") val priceSummary: PriceSummary,
    @SerializedName("data_quality") val dataQuality: DataQualitySummary,
    val technical: TechnicalAnalysis,
    val risk: RiskSummary,
    val news: NewsSummary,
    val fundamentals: FundamentalsSummary,
    @SerializedName("market_context") val marketContext: MarketContextSummary,
    val overall: OverallSummary
)

data class WatchlistItem(
    val symbol: String,
    val companyName: String = "Local watchlist item",
    val lastSetup: String? = null,
    val addedAtMillis: Long = System.currentTimeMillis()
)

data class UserSettings(
    val onboardingComplete: Boolean = false,
    val apiBaseUrl: String = "http://10.0.2.2:8000/",
    val dataMode: String = "live",
    val defaultTimeframe: String = "1D",
    val defaultHorizon: String = "swing",
    val darkMode: Boolean = false
)
