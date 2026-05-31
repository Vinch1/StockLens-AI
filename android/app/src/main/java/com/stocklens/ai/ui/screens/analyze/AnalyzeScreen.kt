package com.stocklens.ai.ui.screens.analyze

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.unit.dp
import com.stocklens.ai.ui.screens.ScreenScaffold
import com.stocklens.ai.viewmodel.AnalyzeUiState

private val timeframes = listOf("15m", "1h", "4h", "1D", "1W")
private val horizons = listOf("short", "swing", "long")
private val assetTypes = listOf("stock", "etf")

@OptIn(ExperimentalLayoutApi::class)
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
    ScreenScaffold(paddingValues = paddingValues) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Text(
                text = "Manual ticker analysis uses backend market data. Screenshot analysis uses approximate candles reconstructed from the image.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(16.dp)
            )
        }

        OutlinedTextField(
            value = analyzeUiState.ticker,
            onValueChange = onTickerChange,
            label = { Text("Ticker symbol") },
            placeholder = { Text("e.g. AAPL") },
            singleLine = true,
            keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Characters),
            modifier = Modifier.fillMaxWidth()
        )

        Text("Asset type", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            assetTypes.forEach { type ->
                FilterChip(
                    selected = analyzeUiState.assetType.equals(type, ignoreCase = true),
                    onClick = { onAssetTypeChange(type) },
                    label = { Text(type.replaceFirstChar { it.uppercase() }) }
                )
            }
        }

        Text("Timeframe", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            timeframes.forEach { tf ->
                FilterChip(
                    selected = analyzeUiState.timeframe.equals(tf, ignoreCase = true),
                    onClick = { onTimeframeChange(tf) },
                    label = { Text(tf) }
                )
            }
        }

        Text("Horizon", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            horizons.forEach { h ->
                FilterChip(
                    selected = analyzeUiState.horizon.equals(h, ignoreCase = true),
                    onClick = { onHorizonChange(h) },
                    label = { Text(h.replaceFirstChar { it.uppercase() }) }
                )
            }
        }

        Row(
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            FilterChip(
                selected = analyzeUiState.includeNews,
                onClick = { onIncludeNewsChange(!analyzeUiState.includeNews) },
                label = { Text("News catalysts") },
                leadingIcon = { if (analyzeUiState.includeNews) Icon(Icons.Default.Analytics, null, Modifier.size(16.dp)) }
            )
            FilterChip(
                selected = analyzeUiState.includeFundamentals,
                onClick = { onIncludeFundamentalsChange(!analyzeUiState.includeFundamentals) },
                label = { Text("Fundamentals") },
                leadingIcon = { if (analyzeUiState.includeFundamentals) Icon(Icons.Default.Description, null, Modifier.size(16.dp)) }
            )
        }

        analyzeUiState.errorMessage?.let { error ->
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Error, null, tint = MaterialTheme.colorScheme.onErrorContainer, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                    Text(error, color = MaterialTheme.colorScheme.onErrorContainer, style = MaterialTheme.typography.bodySmall)
                }
            }
        }

        Button(
            onClick = onAnalyze,
            enabled = !analyzeUiState.isAnalyzing,
            modifier = Modifier.fillMaxWidth().height(52.dp),
            shape = MaterialTheme.shapes.large
        ) {
            if (analyzeUiState.isAnalyzing) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.onPrimary,
                    strokeWidth = 2.dp
                )
                Spacer(Modifier.width(8.dp))
                Text("Analyzing…")
            } else {
                Icon(Icons.Default.Analytics, null, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text("Run Analysis", fontWeight = FontWeight.SemiBold)
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedButton(
                onClick = onScreenshotConfirm,
                modifier = Modifier.weight(1f)
            ) {
                Icon(Icons.Default.CameraAlt, null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(6.dp))
                Text("Screenshot")
            }
            if (analyzeUiState.report != null) {
                FilledTonalButton(
                    onClick = onReport,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.Description, null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("View Report")
                }
            }
        }
    }
}
