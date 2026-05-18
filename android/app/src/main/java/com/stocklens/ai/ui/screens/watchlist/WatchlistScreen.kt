package com.stocklens.ai.ui.screens.watchlist

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.stocklens.ai.ui.screens.EmptyState
import com.stocklens.ai.ui.screens.ScreenScaffold
import com.stocklens.ai.viewmodel.AppUiState

@Composable
fun WatchlistScreen(
    appUiState: AppUiState,
    paddingValues: PaddingValues,
    onAdd: (String) -> Unit,
    onRemove: (String) -> Unit
) {
    var symbol by remember { mutableStateOf("") }
    ScreenScaffold(title = "Watchlist", paddingValues = paddingValues) {
        OutlinedTextField(value = symbol, onValueChange = { symbol = it.uppercase() }, label = { Text("Ticker") })
        Button(onClick = { onAdd(symbol); symbol = "" }) { Text("Add symbol") }
        if (appUiState.watchlist.isEmpty()) {
            EmptyState("No saved symbols. Add one above to persist it locally.")
        } else {
            appUiState.watchlist.forEach { item ->
                Card {
                    androidx.compose.foundation.layout.Column {
                        Text(text = item.symbol)
                        Text(text = item.companyName)
                        Button(onClick = { onRemove(item.symbol) }) { Text("Remove") }
                    }
                }
            }
        }
    }
}
