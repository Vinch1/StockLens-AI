package com.stocklens.ai.ui.screens.analyze

import android.util.Base64
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.UploadFile
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.stocklens.ai.data.model.ScreenshotParseResponse
import com.stocklens.ai.ui.screens.ScreenScaffold
import com.stocklens.ai.ui.theme.Bearish
import com.stocklens.ai.ui.theme.Bullish
import com.stocklens.ai.ui.theme.DarkBearish
import com.stocklens.ai.ui.theme.DarkBullish
import com.stocklens.ai.ui.theme.DarkNeutral
import com.stocklens.ai.ui.theme.LocalDarkTheme
import com.stocklens.ai.ui.theme.Neutral
import com.stocklens.ai.viewmodel.ScreenshotUiState

@Composable
fun ScreenshotConfirmationScreen(
    screenshotUiState: ScreenshotUiState,
    paddingValues: PaddingValues,
    onImageSelected: (String, String?) -> Unit,
    onUseDetectedFields: () -> Unit,
    onDone: () -> Unit
) {
    val context = LocalContext.current
    val imagePicker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching {
            context.contentResolver.openInputStream(uri)?.use { input ->
                Base64.encodeToString(input.readBytes(), Base64.NO_WRAP)
            }
        }.getOrNull()?.let { encoded ->
            onImageSelected(encoded, uri.lastPathSegment)
        }
    }

    ScreenScaffold(paddingValues = paddingValues) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer)
            ) {
                Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.Top) {
                    Icon(
                        Icons.Default.CameraAlt,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onTertiaryContainer,
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(Modifier.width(10.dp))
                    Text(
                        text = "Upload a visible candlestick screenshot. Candle values are reconstructed approximately from the image and must be verified.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onTertiaryContainer
                    )
                }
            }

            Button(
                onClick = { imagePicker.launch("image/*") },
                enabled = !screenshotUiState.isParsing,
                modifier = Modifier.fillMaxWidth().height(52.dp),
                shape = MaterialTheme.shapes.large
            ) {
                if (screenshotUiState.isParsing) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary,
                        strokeWidth = 2.dp
                    )
                    Spacer(Modifier.width(8.dp))
                    Text("Parsing screenshot…")
                } else {
                    Icon(Icons.Default.UploadFile, null, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Choose Screenshot", fontWeight = FontWeight.SemiBold)
                }
            }

            screenshotUiState.selectedFilename?.let { filename ->
                Text(
                    text = filename,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            screenshotUiState.errorMessage?.let { error ->
                ErrorCard(error)
            }

            screenshotUiState.result?.let { result ->
                ScreenshotResultCard(result)

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    FilledTonalButton(
                        onClick = onUseDetectedFields,
                        modifier = Modifier.weight(1f),
                        enabled = !result.detectedTicker.isNullOrBlank() || !result.detectedTimeframe.isNullOrBlank()
                    ) {
                        Icon(Icons.Default.Check, null, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Use Fields")
                    }
                    OutlinedButton(
                        onClick = onDone,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Done")
                    }
                }
            }
        }
    }
}

@Composable
private fun ScreenshotResultCard(result: ScreenshotParseResponse) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Analytics, null, tint = signalColor(result.signal.action), modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text(
                    text = result.signal.action.uppercase(),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = signalColor(result.signal.action)
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = "${result.signal.score}/100 · ${result.signal.confidence}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            MetricRow("Ticker", result.detectedTicker ?: "Not detected")
            MetricRow("Timeframe", result.detectedTimeframe ?: "Not detected")
            MetricRow("Candles", result.extraction.candleCount.toString())
            MetricRow("Calibration", result.extraction.calibrationConfidence)

            Text(result.notes, style = MaterialTheme.typography.bodySmall)
            BulletList("Reasons", result.signal.reasons)
            BulletList("Warnings", result.signal.riskWarnings + result.extraction.warnings)

        }
    }
}

@Composable
private fun ErrorCard(message: String) {
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)) {
        Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Error, null, tint = MaterialTheme.colorScheme.onErrorContainer, modifier = Modifier.size(20.dp))
            Spacer(Modifier.width(8.dp))
            Text(message, color = MaterialTheme.colorScheme.onErrorContainer, style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable
private fun MetricRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Medium)
    }
}

@Composable
private fun BulletList(title: String, items: List<String>) {
    if (items.isEmpty()) return
    Text(title, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.SemiBold)
    items.distinct().take(5).forEach { item ->
        Text("• $item", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun signalColor(action: String): Color {
    val isDark = LocalDarkTheme.current
    return when (action.lowercase()) {
        "buy" -> if (isDark) DarkBullish else Bullish
        "sell" -> if (isDark) DarkBearish else Bearish
        "neutral" -> if (isDark) DarkNeutral else Neutral
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }
}
