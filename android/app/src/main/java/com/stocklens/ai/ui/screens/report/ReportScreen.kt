package com.stocklens.ai.ui.screens.report

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Assessment
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Newspaper
import androidx.compose.material.icons.filled.ShowChart
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.outlined.AccountBalance
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.stocklens.ai.ui.screens.EmptyState
import com.stocklens.ai.ui.screens.ScreenScaffold
import com.stocklens.ai.ui.theme.Bearish
import com.stocklens.ai.ui.theme.Bullish
import com.stocklens.ai.ui.theme.Neutral
import com.stocklens.ai.viewmodel.AnalyzeUiState

@Composable
fun ReportScreen(analyzeUiState: AnalyzeUiState, paddingValues: PaddingValues) {
    ScreenScaffold(title = "Research Report", paddingValues = paddingValues) {
        val report = analyzeUiState.report
        if (report == null) {
            EmptyState(message = "No report generated yet.\nRun an analysis first.")
        } else {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = report.ticker,
                        style = MaterialTheme.typography.headlineLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(Modifier.width(12.dp))
                    Column {
                        Text(
                            text = "${report.timeframe} · ${report.dataMode.uppercase()}",
                            style = MaterialTheme.typography.labelLarge,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                if (report.dataMode == "mock") {
                    InfoBanner("Demo data is being used. Configure a live data provider for real market data.")
                }

                ScoreCard(
                    title = "Overall Score",
                    icon = Icons.Default.Assessment,
                    label = report.overall.label.replace('_', ' '),
                    score = report.overall.score
                )
                Text(
                    text = report.overall.educationalConclusion,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                SectionCard("Technical Setup", Icons.Default.ShowChart) {
                    Text(
                        text = "${report.technical.setup.replace('_', ' ')} (${report.technical.score}/100) · ${report.technical.confidence}",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(Modifier.height(4.dp))
                    Text("Close: ${report.priceSummary.lastClose} (${report.priceSummary.changePct}%)", style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.height(8.dp))
                    val ind = report.technical.indicators
                    Text("SMA 20/50/200: ${ind.sma20} / ${ind.sma50} / ${ind.sma200}", style = MaterialTheme.typography.bodySmall)
                    Text("RSI14: ${ind.rsi14} · MACD: ${ind.macd}/${ind.macdSignal}", style = MaterialTheme.typography.bodySmall)
                    Text("ATR14: ${ind.atr14} · Vol ratio: ${ind.volumeRatio}", style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.height(8.dp))
                    Text("Support: ${report.technical.supportResistance.support.joinToString()}", style = MaterialTheme.typography.bodySmall, color = Bullish)
                    Text("Resistance: ${report.technical.supportResistance.resistance.joinToString()}", style = MaterialTheme.typography.bodySmall, color = Bearish)
                }

                SectionCard("Evidence", Icons.Default.Info) {
                    report.technical.evidence.forEach { item ->
                        Text("• $item", style = MaterialTheme.typography.bodySmall)
                    }
                }

                SectionCard("News Catalysts", Icons.Default.Newspaper) {
                    Text("${report.news.sentiment} · Score ${report.news.score}/100", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                    Spacer(Modifier.height(4.dp))
                    Text(report.news.summary, style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.height(4.dp))
                    report.news.items.take(3).forEach { item ->
                        Text("• ${item.title} — ${item.source} (${item.catalystType})", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }

                SectionCard("Fundamentals", Icons.Outlined.AccountBalance) {
                    Text("${report.fundamentals.quality} · Score ${report.fundamentals.score}/100", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                    Spacer(Modifier.height(4.dp))
                    Text(report.fundamentals.summary, style = MaterialTheme.typography.bodySmall)
                }

                SectionCard("Risk Factors", Icons.Default.Warning) {
                    report.technical.risks.forEach { risk ->
                        Text("• $risk", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.error)
                    }
                }

                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Disclaimer", style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(4.dp))
                        Text(report.disclaimer, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(Modifier.height(4.dp))
                        Text("Generated: ${report.generatedAt}", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
    }
}

@Composable
private fun ScoreCard(title: String, icon: ImageVector, label: String, score: Int) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            }
            Spacer(Modifier.height(12.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Bold,
                    color = scoreColor(score)
                )
                Text(
                    text = "$score/100",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = scoreColor(score)
                )
            }
            Spacer(Modifier.height(8.dp))
            LinearProgressIndicator(
                progress = { score / 100f },
                modifier = Modifier.fillMaxWidth(),
                color = scoreColor(score),
                trackColor = MaterialTheme.colorScheme.outline,
                strokeCap = StrokeCap.Round
            )
        }
    }
}

@Composable
private fun SectionCard(title: String, icon: ImageVector, content: @Composable () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            }
            Spacer(Modifier.height(8.dp))
            content()
        }
    }
}

@Composable
private fun InfoBanner(message: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer)
    ) {
        Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Info, null, tint = MaterialTheme.colorScheme.onTertiaryContainer, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(8.dp))
            Text(message, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onTertiaryContainer)
        }
    }
}

private fun scoreColor(score: Int): Color {
    return when {
        score >= 70 -> Bullish
        score >= 40 -> Neutral
        else -> Bearish
    }
}
