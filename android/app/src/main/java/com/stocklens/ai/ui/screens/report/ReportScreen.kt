package com.stocklens.ai.ui.screens.report

import android.app.Activity
import android.content.ContentValues
import android.content.Context
import android.content.ContextWrapper
import android.graphics.Bitmap
import android.graphics.Canvas
import android.media.MediaScannerConnection
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
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
import androidx.compose.material.icons.filled.Public
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.ShowChart
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.outlined.BarChart
import androidx.compose.material.icons.outlined.AccountBalance
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.CompositionContext
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCompositionContext
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.stocklens.ai.data.model.AnalyzeResponse
import com.stocklens.ai.ui.screens.EmptyState
import com.stocklens.ai.ui.theme.Bearish
import com.stocklens.ai.ui.theme.Bullish
import com.stocklens.ai.ui.theme.DarkBearish
import com.stocklens.ai.ui.theme.DarkBullish
import com.stocklens.ai.ui.theme.DarkNeutral
import com.stocklens.ai.ui.theme.LocalDarkTheme
import com.stocklens.ai.ui.theme.Neutral
import com.stocklens.ai.viewmodel.AnalyzeUiState
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import kotlin.math.roundToInt
import kotlin.math.sqrt
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun ReportScreen(analyzeUiState: AnalyzeUiState, paddingValues: PaddingValues) {
    val report = analyzeUiState.report
    if (report == null) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ReportHeader()
            EmptyState(message = "No report generated yet.\nRun an analysis first.")
        }
    } else {
        val context = LocalContext.current
        val rootView = LocalView.current
        val parentCompositionContext = rememberCompositionContext()
        val coroutineScope = rememberCoroutineScope()
        var isSavingReportImage by remember { mutableStateOf(false) }
        val backgroundColor = MaterialTheme.colorScheme.background

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 20.dp)
                .background(backgroundColor)
                .verticalScroll(rememberScrollState()),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(backgroundColor),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                ReportHeader(
                    isSaving = isSavingReportImage,
                    onSaveImage = {
                        if (!isSavingReportImage) {
                            coroutineScope.launch {
                                isSavingReportImage = true
                                try {
                                    val bitmap = renderFullReportBitmap(
                                        context = context,
                                        rootView = rootView,
                                        parentCompositionContext = parentCompositionContext,
                                        report = report
                                    )
                                    try {
                                        saveReportImage(context, bitmap, report.ticker)
                                    } finally {
                                        bitmap.recycle()
                                    }
                                    Toast.makeText(context, "Report image saved", Toast.LENGTH_SHORT).show()
                                } catch (exc: Exception) {
                                    Toast.makeText(
                                        context,
                                        "Could not save report image: ${exc.message ?: "unknown error"}",
                                        Toast.LENGTH_LONG
                                    ).show()
                                } finally {
                                    isSavingReportImage = false
                                }
                            }
                        }
                    }
                )

                ReportBody(report)
            }
            Spacer(Modifier.height(8.dp))
        }
    }
}

@Composable
private fun ReportBody(report: AnalyzeResponse) {
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

    if (report.dataMode == "unavailable" || report.dataMode == "mixed") {
        InfoBanner("Some provider data is unavailable. Review provider status and verify data before drawing conclusions.")
    }

    ScoreCard(
        title = "Overall Score",
        icon = Icons.Default.Assessment,
        label = report.overall.label.replace('_', ' '),
        score = report.overall.score
    )
    Text(
        text = report.overall.conclusion,
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant
    )

    SectionCard("Data Quality", Icons.Outlined.BarChart) {
        ScoreLine("Quality score", report.dataQuality.score)
        Spacer(Modifier.height(8.dp))
        MetricRow("Status", report.dataQuality.status)
        MetricRow("Bars", report.dataQuality.barsCount.toString())
        MetricRow("Latest", report.dataQuality.latestTimestamp ?: "Unavailable")
        WarningList(report.dataQuality.warnings)
    }

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
        Text("Support: ${report.technical.supportResistance.support.joinToString()}", style = MaterialTheme.typography.bodySmall, color = scoreColor(80))
        Text("Resistance: ${report.technical.supportResistance.resistance.joinToString()}", style = MaterialTheme.typography.bodySmall, color = scoreColor(20))
        Spacer(Modifier.height(12.dp))
        SubScoreLine("Trend", report.technical.trendScore)
        SubScoreLine("Momentum", report.technical.momentumScore)
        SubScoreLine("Structure", report.technical.structureScore)
        SubScoreLine("Volume", report.technical.volumeScore)
        SubScoreLine("Volatility", report.technical.volatilityScore)
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
        Spacer(Modifier.height(12.dp))
        SubScoreLine("Growth", report.fundamentals.growthScore)
        SubScoreLine("Profitability", report.fundamentals.profitabilityScore)
        SubScoreLine("Balance sheet", report.fundamentals.balanceSheetScore)
        SubScoreLine("Valuation", report.fundamentals.valuationScore)
        SubScoreLine("Cash flow", report.fundamentals.cashFlowScore)
        Spacer(Modifier.height(8.dp))
        MetricRow("Revenue growth", formatMetric(report.fundamentals.metrics.revenueGrowth, "%"))
        MetricRow("Earnings growth", formatMetric(report.fundamentals.metrics.earningsGrowth, "%"))
        MetricRow("Debt/equity", formatMetric(report.fundamentals.metrics.debtToEquity))
        MetricRow("Forward P/E", formatMetric(report.fundamentals.metrics.forwardPe))
    }

    SectionCard("Market Context", Icons.Default.Public) {
        ScoreLine("Context score", report.marketContext.score)
        Spacer(Modifier.height(8.dp))
        MetricRow("Benchmark", report.marketContext.benchmark)
        MetricRow("20D relative strength", formatMetric(report.marketContext.relativeStrength20d, "%"))
        MetricRow("60D relative strength", formatMetric(report.marketContext.relativeStrength60d, "%"))
        Spacer(Modifier.height(4.dp))
        Text(report.marketContext.summary, style = MaterialTheme.typography.bodySmall)
    }

    SectionCard("Risk Factors", Icons.Default.Warning) {
        Text("${report.risk.level} · Score ${report.risk.score}/100", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(8.dp))
        MetricRow("ATR %", formatMetric(report.risk.atrPct, "%"))
        MetricRow("20D volatility", formatMetric(report.risk.realizedVolatility20d, "%"))
        MetricRow("60D volatility", formatMetric(report.risk.realizedVolatility60d, "%"))
        MetricRow("60D max drawdown", formatMetric(report.risk.maxDrawdown60d, "%"))
        MetricRow("20D avg dollar volume", formatCurrency(report.risk.averageDollarVolume20d))
        WarningList(report.risk.warnings)
        Spacer(Modifier.height(8.dp))
        report.technical.risks.forEach { risk ->
            Text("• $risk", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.error)
        }
    }

    Text("Generated: ${report.generatedAt}", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
}

@Composable
private fun ReportHeader(
    isSaving: Boolean = false,
    onSaveImage: (() -> Unit)? = null
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "Research Report",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )
        if (onSaveImage != null) {
            IconButton(
                onClick = onSaveImage,
                enabled = !isSaving
            ) {
                if (isSaving) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp
                    )
                } else {
                    Icon(
                        imageVector = Icons.Default.Share,
                        contentDescription = "Save report image"
                    )
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
                progress = { score.coerceIn(0, 100) / 100f },
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

@Composable
private fun scoreColor(score: Int): Color {
    val isDark = LocalDarkTheme.current
    return when {
        score >= 70 -> if (isDark) DarkBullish else Bullish
        score >= 40 -> if (isDark) DarkNeutral else Neutral
        else -> if (isDark) DarkBearish else Bearish
    }
}

@Composable
private fun ScoreLine(label: String, score: Int) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(label, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Medium)
            Text("$score/100", style = MaterialTheme.typography.labelLarge, color = scoreColor(score))
        }
        LinearProgressIndicator(
            progress = { score.coerceIn(0, 100) / 100f },
            modifier = Modifier.fillMaxWidth(),
            color = scoreColor(score),
            trackColor = MaterialTheme.colorScheme.outlineVariant,
            strokeCap = StrokeCap.Round
        )
    }
}

@Composable
private fun SubScoreLine(label: String, score: Int?) {
    if (score == null) return
    ScoreLine(label, score)
    Spacer(Modifier.height(8.dp))
}

@Composable
private fun MetricRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.Top
    ) {
        Text(
            text = label,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.width(16.dp))
        Text(
            text = value,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.Medium,
            textAlign = TextAlign.End
        )
    }
}

@Composable
private fun WarningList(warnings: List<String>) {
    if (warnings.isEmpty()) return
    Spacer(Modifier.height(8.dp))
    warnings.forEach { warning ->
        Text("• $warning", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.error)
    }
}

private fun formatMetric(value: Double?, suffix: String = ""): String {
    return value?.let { "%.2f%s".format(it, suffix) } ?: "Unavailable"
}

private fun formatCurrency(value: Double?): String {
    return value?.let { "\$%,.0f".format(it) } ?: "Unavailable"
}

private const val MAX_REPORT_EXPORT_PIXELS = 24_000_000

private suspend fun renderFullReportBitmap(
    context: Context,
    rootView: View,
    parentCompositionContext: CompositionContext,
    report: AnalyzeResponse
): Bitmap = withContext(Dispatchers.Main.immediate) {
    val activity = rootView.context.findActivity()
        ?: context.findActivity()
        ?: throw IOException("Activity window is unavailable")
    val decorView = activity.window.decorView as? ViewGroup
        ?: throw IOException("Window decor view is unavailable")
    val exportWidth = rootView.width
        .takeIf { it > 0 }
        ?: decorView.width.takeIf { it > 0 }
        ?: throw IOException("Report width is not ready")

    val composeView = ComposeView(context).apply {
        setParentCompositionContext(parentCompositionContext)
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS
        translationX = -exportWidth.toFloat() * 2f
        setContent {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.background)
                    .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                ReportHeader()
                ReportBody(report)
                Spacer(Modifier.height(8.dp))
            }
        }
    }

    try {
        decorView.addView(
            composeView,
            ViewGroup.LayoutParams(exportWidth, ViewGroup.LayoutParams.WRAP_CONTENT)
        )

        val widthSpec = View.MeasureSpec.makeMeasureSpec(exportWidth, View.MeasureSpec.EXACTLY)
        val heightSpec = View.MeasureSpec.makeMeasureSpec(0, View.MeasureSpec.UNSPECIFIED)
        composeView.measure(widthSpec, heightSpec)
        val measuredHeight = composeView.measuredHeight
        if (measuredHeight <= 0) {
            throw IOException("Report export measured empty")
        }
        composeView.layout(0, 0, exportWidth, measuredHeight)

        val (bitmapWidth, bitmapHeight) = scaledReportExportSize(exportWidth, measuredHeight)
        val bitmap = Bitmap.createBitmap(bitmapWidth, bitmapHeight, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        val scale = bitmapWidth.toFloat() / exportWidth.toFloat()
        canvas.scale(scale, scale)
        composeView.draw(canvas)
        bitmap
    } finally {
        decorView.removeView(composeView)
    }
}

private fun scaledReportExportSize(width: Int, height: Int): Pair<Int, Int> {
    val pixelCount = width.toLong() * height.toLong()
    if (pixelCount <= MAX_REPORT_EXPORT_PIXELS) {
        return width to height
    }
    val scale = sqrt(MAX_REPORT_EXPORT_PIXELS.toDouble() / pixelCount.toDouble())
    return (width * scale).roundToInt().coerceAtLeast(1) to
        (height * scale).roundToInt().coerceAtLeast(1)
}

private suspend fun saveReportImage(
    context: Context,
    bitmap: Bitmap,
    ticker: String
): Uri = withContext(Dispatchers.IO) {
    val filename = reportImageFileName(ticker)
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        saveReportImageToMediaStore(context, bitmap, filename)
    } else {
        saveReportImageToAppPictures(context, bitmap, filename)
    }
}

private fun saveReportImageToMediaStore(
    context: Context,
    bitmap: Bitmap,
    filename: String
): Uri {
    val resolver = context.contentResolver
    val values = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, filename)
        put(MediaStore.Images.Media.MIME_TYPE, "image/png")
        put(MediaStore.Images.Media.RELATIVE_PATH, "${Environment.DIRECTORY_PICTURES}/StockLens AI")
        put(MediaStore.Images.Media.IS_PENDING, 1)
    }
    val collection = MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
    val uri = resolver.insert(collection, values)
        ?: throw IOException("Could not create image entry")

    try {
        resolver.openOutputStream(uri)?.use { output ->
            if (!bitmap.compress(Bitmap.CompressFormat.PNG, 100, output)) {
                throw IOException("Bitmap compression failed")
            }
        } ?: throw IOException("Could not open image output stream")

        val publishedValues = ContentValues().apply {
            put(MediaStore.Images.Media.IS_PENDING, 0)
        }
        resolver.update(uri, publishedValues, null, null)
        return uri
    } catch (exc: Exception) {
        resolver.delete(uri, null, null)
        throw exc
    }
}

private fun saveReportImageToAppPictures(
    context: Context,
    bitmap: Bitmap,
    filename: String
): Uri {
    val directory = File(context.getExternalFilesDir(Environment.DIRECTORY_PICTURES), "StockLens AI")
    if (!directory.exists() && !directory.mkdirs()) {
        throw IOException("Could not create image folder")
    }
    val file = File(directory, filename)
    FileOutputStream(file).use { output ->
        if (!bitmap.compress(Bitmap.CompressFormat.PNG, 100, output)) {
            throw IOException("Bitmap compression failed")
        }
    }
    MediaScannerConnection.scanFile(
        context,
        arrayOf(file.absolutePath),
        arrayOf("image/png"),
        null
    )
    return Uri.fromFile(file)
}

private fun reportImageFileName(ticker: String): String {
    val safeTicker = ticker.replace(Regex("[^A-Za-z0-9._-]"), "_")
    return "StockLens_${safeTicker}_${System.currentTimeMillis()}.png"
}

private tailrec fun Context.findActivity(): Activity? {
    return when (this) {
        is Activity -> this
        is ContextWrapper -> baseContext.findActivity()
        else -> null
    }
}
