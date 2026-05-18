package com.stocklens.ai.data.repository

import com.stocklens.ai.data.local.PreferencesStore
import com.stocklens.ai.data.model.AnalyzeRequest
import com.stocklens.ai.data.model.AnalyzeResponse
import com.stocklens.ai.data.model.FundamentalMetrics
import com.stocklens.ai.data.model.FundamentalsSummary
import com.stocklens.ai.data.model.IndicatorSummary
import com.stocklens.ai.data.model.NewsSummary
import com.stocklens.ai.data.model.OverallSummary
import com.stocklens.ai.data.model.PriceSummary
import com.stocklens.ai.data.model.SupportResistance
import com.stocklens.ai.data.model.TechnicalAnalysis
import com.stocklens.ai.data.model.UserSettings
import com.stocklens.ai.data.model.WatchlistItem
import com.stocklens.ai.data.remote.StockLensApi
import kotlinx.coroutines.flow.Flow

class StockLensRepository(
    private val api: StockLensApi,
    private val preferencesStore: PreferencesStore
) {
    val settings: Flow<UserSettings> = preferencesStore.settings
    val watchlist: Flow<List<WatchlistItem>> = preferencesStore.watchlist

    suspend fun analyze(request: AnalyzeRequest): AnalyzeResponse = api.analyze(request.copy(ticker = request.ticker.uppercase()))

    suspend fun saveSettings(settings: UserSettings) = preferencesStore.saveSettings(settings)
    suspend fun addWatchlistSymbol(symbol: String) = preferencesStore.addWatchlistSymbol(symbol)
    suspend fun removeWatchlistSymbol(symbol: String) = preferencesStore.removeWatchlistSymbol(symbol)

    fun offlineErrorReport(ticker: String, message: String): AnalyzeResponse = AnalyzeResponse(
        ticker = ticker.uppercase(),
        assetType = "stock",
        timeframe = "1D",
        horizon = "swing",
        generatedAt = "Offline error state",
        dataMode = "mock",
        priceSummary = PriceSummary(lastClose = 0.0, changePct = 0.0, volume = 0),
        technical = TechnicalAnalysis(
            setup = "needs_more_confirmation",
            score = 0,
            confidence = "low",
            indicators = IndicatorSummary(),
            supportResistance = SupportResistance(),
            evidence = listOf("Backend unavailable: $message"),
            risks = listOf("Analysis may be incomplete or delayed. Verify data before making decisions.")
        ),
        news = NewsSummary(sentiment = "neutral", score = 0, items = emptyList(), summary = "No live news was retrieved."),
        fundamentals = FundamentalsSummary(quality = "unavailable", score = 0, metrics = FundamentalMetrics(), summary = "Fundamental data was not retrieved."),
        overall = OverallSummary(
            label = "needs_more_confirmation",
            score = 0,
            confidence = "low",
            educationalConclusion = "Unable to complete the research summary. This is not financial advice; verify with configured data sources."
        ),
        disclaimer = "Educational information only. Not financial advice. Markets involve risk. Verify all data before making decisions."
    )
}
