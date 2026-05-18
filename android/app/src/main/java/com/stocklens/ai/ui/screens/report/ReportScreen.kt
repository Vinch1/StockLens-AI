package com.stocklens.ai.ui.screens.report

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.material3.Card
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import com.stocklens.ai.ui.screens.EmptyState
import com.stocklens.ai.ui.screens.ScreenScaffold
import com.stocklens.ai.viewmodel.AnalyzeUiState

@Composable
fun ReportScreen(analyzeUiState: AnalyzeUiState, paddingValues: PaddingValues) {
    ScreenScaffold(title = "Research report", paddingValues = paddingValues) {
        val report = analyzeUiState.report
        if (report == null) {
            EmptyState(message = "No report generated yet.")
        } else {
            Text(text = "${report.ticker} • ${report.timeframe} • ${report.dataMode.uppercase()} data", style = MaterialTheme.typography.headlineSmall)
            if (report.dataMode == "mock") Text("Demo data is being used. Configure a live data provider for real market data.")
            Card {
                Text(text = "Overall: ${report.overall.label.replace('_', ' ')}")
                LinearProgressIndicator(progress = { report.overall.score / 100f })
                Text(text = report.overall.educationalConclusion)
            }
            Card {
                Text(text = "Technical setup: ${report.technical.setup.replace('_', ' ')} (${report.technical.score}/100, ${report.technical.confidence})")
                Text(text = "Close: ${report.priceSummary.lastClose} (${report.priceSummary.changePct}%)")
                Text(text = "SMA20 ${report.technical.indicators.sma20} • SMA50 ${report.technical.indicators.sma50} • SMA200 ${report.technical.indicators.sma200}")
                Text(text = "RSI14 ${report.technical.indicators.rsi14} • MACD ${report.technical.indicators.macd}/${report.technical.indicators.macdSignal}")
                Text(text = "ATR14 ${report.technical.indicators.atr14} • Volume ratio ${report.technical.indicators.volumeRatio}")
            }
            Card { Text(text = "Evidence\n${report.technical.evidence.joinToString("\n") { "• $it" }}") }
            Card { Text(text = "Support ${report.technical.supportResistance.support.joinToString()}\nResistance ${report.technical.supportResistance.resistance.joinToString()}") }
            Card { Text(text = "News (${report.news.sentiment}, score ${report.news.score})\n${report.news.summary}\n${report.news.items.take(3).joinToString("\n") { "• ${it.title} — ${it.source} (${it.catalystType})" }}") }
            Card { Text(text = "Fundamentals (${report.fundamentals.quality}, score ${report.fundamentals.score})\n${report.fundamentals.summary}") }
            Card { Text(text = "Risk factors\n${report.technical.risks.joinToString("\n") { "• $it" }}") }
            Text(text = "This analysis is based on available configured data and may be incomplete or delayed. It does not predict future performance.")
            Text(text = report.disclaimer)
            Text(text = "Generated: ${report.generatedAt}")
        }
    }
}
