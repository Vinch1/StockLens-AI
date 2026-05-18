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
    val risks: List<String>
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
    val summary: String
)

data class OverallSummary(
    val label: String,
    val score: Int,
    val confidence: String,
    @SerializedName("educational_conclusion") val educationalConclusion: String
)

data class AnalyzeResponse(
    val ticker: String,
    @SerializedName("asset_type") val assetType: String,
    val timeframe: String,
    val horizon: String,
    @SerializedName("generated_at") val generatedAt: String,
    @SerializedName("data_mode") val dataMode: String,
    @SerializedName("price_summary") val priceSummary: PriceSummary,
    val technical: TechnicalAnalysis,
    val news: NewsSummary,
    val fundamentals: FundamentalsSummary,
    val overall: OverallSummary,
    val disclaimer: String
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
    val dataMode: String = "mock",
    val defaultTimeframe: String = "1D",
    val defaultHorizon: String = "swing",
    val darkMode: Boolean = false
)
