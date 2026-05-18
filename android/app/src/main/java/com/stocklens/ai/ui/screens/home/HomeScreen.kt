package com.stocklens.ai.ui.screens.home

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.stocklens.ai.ui.screens.EmptyState
import com.stocklens.ai.ui.screens.ScreenScaffold
import com.stocklens.ai.viewmodel.AppUiState

@Composable
fun HomeScreen(
    appUiState: AppUiState,
    paddingValues: PaddingValues,
    onAnalyze: () -> Unit,
    onWatchlist: () -> Unit
) {
    ScreenScaffold(title = "StockLens AI", paddingValues = paddingValues) {
        Card(modifier = Modifier.fillMaxWidth()) {
            androidx.compose.foundation.layout.Column {
                Text(text = "Market snapshot", style = MaterialTheme.typography.titleLarge)
                Text(text = "Manual ticker analysis calls the StockLens AI backend and labels mock data clearly.")
            }
        }
        Button(onClick = onAnalyze) { Text(text = "Analyze a stock") }
        if (appUiState.watchlist.isEmpty()) {
            EmptyState("Your local watchlist is empty.", "Open watchlist", onWatchlist)
        } else {
            Text(text = "Watching ${appUiState.watchlist.size} symbols", style = MaterialTheme.typography.titleMedium)
            appUiState.watchlist.take(5).forEach { item -> Text(text = item.symbol) }
        }
    }
}
