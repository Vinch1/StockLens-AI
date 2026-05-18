package com.stocklens.ai.ui.screens.analyze

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.input.KeyboardCapitalization
import com.stocklens.ai.ui.screens.ScreenScaffold
import com.stocklens.ai.viewmodel.AnalyzeUiState

@Composable
fun AnalyzeScreen(
    analyzeUiState: AnalyzeUiState,
    paddingValues: PaddingValues,
    onTickerChange: (String) -> Unit,
    onAssetTypeChange: (String) -> Unit,
    onTimeframeChange: (String) -> Unit,
    onHorizonChange: (String) -> Unit,
    onIncludeNewsChange: (Boolean) -> Unit,
    onIncludeFundamentalsChange: (Boolean) -> Unit,
    onAnalyze: () -> Unit,
    onScreenshotConfirm: () -> Unit,
    onReport: () -> Unit
) {
    ScreenScaffold(title = "Analyze", paddingValues = paddingValues) {
        Text("Manual ticker analysis uses backend market data, not screenshots, and is educational only.")
        OutlinedTextField(
            value = analyzeUiState.ticker,
            onValueChange = onTickerChange,
            label = { Text("Ticker") },
            keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Characters)
        )
        OutlinedTextField(value = analyzeUiState.assetType, onValueChange = onAssetTypeChange, label = { Text("Asset type: stock or etf") })
        OutlinedTextField(value = analyzeUiState.timeframe, onValueChange = onTimeframeChange, label = { Text("Timeframe: 15m, 1h, 4h, 1D, 1W") })
        OutlinedTextField(value = analyzeUiState.horizon, onValueChange = onHorizonChange, label = { Text("Horizon: short, swing, long") })
        androidx.compose.foundation.layout.Row { Checkbox(checked = analyzeUiState.includeNews, onCheckedChange = onIncludeNewsChange); Text("Include news catalysts") }
        androidx.compose.foundation.layout.Row { Checkbox(checked = analyzeUiState.includeFundamentals, onCheckedChange = onIncludeFundamentalsChange); Text("Include fundamentals") }
        analyzeUiState.errorMessage?.let { Text(text = it) }
        Button(onClick = onAnalyze, enabled = !analyzeUiState.isAnalyzing) {
            if (analyzeUiState.isAnalyzing) CircularProgressIndicator() else Text("Analyze")
        }
        Button(onClick = onScreenshotConfirm) { Text("Screenshot-assisted input") }
        if (analyzeUiState.report != null) {
            Button(onClick = onReport) { Text("View latest report") }
        }
    }
}
