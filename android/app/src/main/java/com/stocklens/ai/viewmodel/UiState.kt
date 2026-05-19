package com.stocklens.ai.viewmodel

import com.stocklens.ai.data.model.AnalyzeResponse
import com.stocklens.ai.data.model.ScreenshotParseResponse
import com.stocklens.ai.data.model.UserSettings
import com.stocklens.ai.data.model.WatchlistItem

data class AppUiState(
    val settings: UserSettings = UserSettings(),
    val watchlist: List<WatchlistItem> = emptyList(),
    val isLoading: Boolean = true,
    val errorMessage: String? = null
)

data class AnalyzeUiState(
    val ticker: String = "",
    val assetType: String = "stock",
    val timeframe: String = "1D",
    val horizon: String = "swing",
    val includeNews: Boolean = true,
    val includeFundamentals: Boolean = true,
    val isAnalyzing: Boolean = false,
    val report: AnalyzeResponse? = null,
    val errorMessage: String? = null
)

data class ScreenshotUiState(
    val isParsing: Boolean = false,
    val result: ScreenshotParseResponse? = null,
    val errorMessage: String? = null,
    val selectedFilename: String? = null
)
