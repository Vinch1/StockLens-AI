package com.stocklens.ai.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.stocklens.ai.data.model.AnalyzeRequest
import com.stocklens.ai.data.model.AnalyzeResponse
import com.stocklens.ai.data.model.UserSettings
import com.stocklens.ai.data.remote.NetworkMonitor
import com.stocklens.ai.data.repository.StockLensRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class StockLensViewModel(
    private val repository: StockLensRepository,
    networkMonitor: NetworkMonitor
) : ViewModel() {
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

    private val _screenshotUiState = MutableStateFlow(ScreenshotUiState())
    val screenshotUiState: StateFlow<ScreenshotUiState> = _screenshotUiState

    private var analyzeJob: Job? = null
    private var screenshotJob: Job? = null

    private var lastAnalyzeRequest: AnalyzeRequest? = null
    private var lastAnalyzeResponse: AnalyzeResponse? = null

    private var isOnline = true

    init {
        viewModelScope.launch {
            networkMonitor.isOnline.collect { isOnline = it }
        }
    }

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
            showError("Enter a ticker symbol.")
            return
        }
        val request = AnalyzeRequest(
            ticker = state.ticker,
            assetType = state.assetType,
            timeframe = state.timeframe,
            horizon = state.horizon,
            includeNews = state.includeNews,
            includeFundamentals = state.includeFundamentals
        )
        if (request == lastAnalyzeRequest && lastAnalyzeResponse != null) {
            _analyzeUiState.update { it.copy(report = lastAnalyzeResponse) }
            return
        }
        if (!isOnline) {
            _analyzeUiState.update {
                it.copy(errorMessage = "No internet connection. Check your network settings.")
            }
            return
        }
        analyzeJob?.cancel()
        analyzeJob = viewModelScope.launch {
            _analyzeUiState.update { it.copy(isAnalyzing = true, errorMessage = null) }
            runCatching { repository.analyze(request) }
                .onSuccess { report ->
                    lastAnalyzeRequest = request
                    lastAnalyzeResponse = report
                    _analyzeUiState.update { it.copy(isAnalyzing = false, report = report) }
                    repository.addWatchlistSymbol(report.ticker)
                }
                .onFailure { throwable ->
                    if (throwable is CancellationException) return@onFailure
                    showError(throwable.message ?: "Unable to analyze ticker.")
                    _analyzeUiState.update { it.copy(isAnalyzing = false) }
                }
        }
    }

    private fun showError(message: String) {
        _analyzeUiState.update { it.copy(errorMessage = message) }
        viewModelScope.launch {
            delay(5_000)
            _analyzeUiState.update {
                if (it.errorMessage == message) it.copy(errorMessage = null) else it
            }
        }
    }

    fun parseScreenshot(imageBase64: String, filename: String?) {
        screenshotJob?.cancel()
        screenshotJob = viewModelScope.launch {
            _screenshotUiState.update {
                it.copy(isParsing = true, errorMessage = null, selectedFilename = filename)
            }
            runCatching {
                repository.parseScreenshot(imageBase64 = imageBase64, filename = filename)
            }.onSuccess { result ->
                _screenshotUiState.update { it.copy(isParsing = false, result = result) }
            }.onFailure { throwable ->
                if (throwable is CancellationException) return@onFailure
                _screenshotUiState.update {
                    it.copy(isParsing = false, errorMessage = throwable.message ?: "Unable to parse screenshot.")
                }
            }
        }
    }

    fun applyScreenshotDetectionToForm() {
        val result = screenshotUiState.value.result ?: return
        val ticker = result.detectedTicker.orEmpty()
        val timeframe = result.detectedTimeframe ?: analyzeUiState.value.timeframe
        if (ticker.isBlank()) {
            updateAnalyzeForm(timeframe = timeframe)
        } else {
            updateAnalyzeForm(ticker = ticker, timeframe = timeframe)
        }
    }
}

class StockLensViewModelFactory(
    private val repository: StockLensRepository,
    private val networkMonitor: NetworkMonitor
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(StockLensViewModel::class.java)) {
            return StockLensViewModel(repository, networkMonitor) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
