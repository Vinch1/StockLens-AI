package com.stocklens.ai.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.stocklens.ai.data.model.AnalyzeRequest
import com.stocklens.ai.data.model.UserSettings
import com.stocklens.ai.data.repository.StockLensRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class StockLensViewModel(private val repository: StockLensRepository) : ViewModel() {
    val appUiState: StateFlow<AppUiState> = combine(
        repository.settings,
        repository.watchlist
    ) { settings, watchlist ->
        AppUiState(settings = settings, watchlist = watchlist, isLoading = false)
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = AppUiState()
    )

    private val _analyzeUiState = MutableStateFlow(AnalyzeUiState())
    val analyzeUiState: StateFlow<AnalyzeUiState> = _analyzeUiState

    fun updateAnalyzeForm(
        ticker: String = analyzeUiState.value.ticker,
        assetType: String = analyzeUiState.value.assetType,
        timeframe: String = analyzeUiState.value.timeframe,
        horizon: String = analyzeUiState.value.horizon,
        includeNews: Boolean = analyzeUiState.value.includeNews,
        includeFundamentals: Boolean = analyzeUiState.value.includeFundamentals
    ) {
        _analyzeUiState.update {
            it.copy(
                ticker = ticker.uppercase(),
                assetType = assetType,
                timeframe = timeframe,
                horizon = horizon,
                includeNews = includeNews,
                includeFundamentals = includeFundamentals
            )
        }
    }

    fun completeOnboarding() {
        viewModelScope.launch {
            repository.saveSettings(appUiState.value.settings.copy(onboardingComplete = true))
        }
    }

    fun saveSettings(settings: UserSettings) {
        viewModelScope.launch { repository.saveSettings(settings) }
    }

    fun addWatchlistSymbol(symbol: String) {
        if (symbol.isBlank()) return
        viewModelScope.launch { repository.addWatchlistSymbol(symbol) }
    }

    fun removeWatchlistSymbol(symbol: String) {
        viewModelScope.launch { repository.removeWatchlistSymbol(symbol) }
    }

    fun analyze() {
        val state = analyzeUiState.value
        if (state.ticker.isBlank()) {
            _analyzeUiState.update { it.copy(errorMessage = "Enter a ticker symbol.") }
            return
        }
        viewModelScope.launch {
            _analyzeUiState.update { it.copy(isAnalyzing = true, errorMessage = null) }
            runCatching {
                repository.analyze(
                    AnalyzeRequest(
                        ticker = state.ticker,
                        assetType = state.assetType,
                        timeframe = state.timeframe,
                        horizon = state.horizon,
                        includeNews = state.includeNews,
                        includeFundamentals = state.includeFundamentals
                    )
                )
            }.onSuccess { report ->
                _analyzeUiState.update { it.copy(isAnalyzing = false, report = report) }
                repository.addWatchlistSymbol(report.ticker)
            }.onFailure { throwable ->
                _analyzeUiState.update {
                    it.copy(isAnalyzing = false, errorMessage = throwable.message ?: "Unable to analyze ticker.")
                }
            }
        }
    }
}

class StockLensViewModelFactory(
    private val repository: StockLensRepository
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(StockLensViewModel::class.java)) {
            return StockLensViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
