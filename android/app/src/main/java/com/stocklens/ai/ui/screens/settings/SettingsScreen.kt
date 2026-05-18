package com.stocklens.ai.ui.screens.settings

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.stocklens.ai.data.model.UserSettings
import com.stocklens.ai.ui.screens.ScreenScaffold

@Composable
fun SettingsScreen(
    settings: UserSettings,
    paddingValues: PaddingValues,
    onSave: (UserSettings) -> Unit
) {
    var apiBaseUrl by remember(settings.apiBaseUrl) { mutableStateOf(settings.apiBaseUrl) }
    var dataMode by remember(settings.dataMode) { mutableStateOf(settings.dataMode) }
    var timeframe by remember(settings.defaultTimeframe) { mutableStateOf(settings.defaultTimeframe) }
    var horizon by remember(settings.defaultHorizon) { mutableStateOf(settings.defaultHorizon) }
    var darkMode by remember(settings.darkMode) { mutableStateOf(settings.darkMode) }

    ScreenScaffold(title = "Settings & About", paddingValues = paddingValues) {
        OutlinedTextField(value = apiBaseUrl, onValueChange = { apiBaseUrl = it }, label = { Text("API base URL") })
        OutlinedTextField(value = dataMode, onValueChange = { dataMode = it }, label = { Text("Data mode: mock/live") })
        OutlinedTextField(value = timeframe, onValueChange = { timeframe = it }, label = { Text("Default timeframe") })
        OutlinedTextField(value = horizon, onValueChange = { horizon = it }, label = { Text("Default horizon") })
        Card {
            androidx.compose.foundation.layout.Row {
                Text(text = "Dark mode")
                Switch(checked = darkMode, onCheckedChange = { darkMode = it })
            }
        }
        Button(
            onClick = {
                onSave(
                    settings.copy(
                        apiBaseUrl = apiBaseUrl,
                        dataMode = dataMode,
                        defaultTimeframe = timeframe,
                        defaultHorizon = horizon,
                        darkMode = darkMode
                    )
                )
            }
        ) { Text("Save settings") }
        Text(text = "StockLens AI provides educational research summaries only. It is not financial, investment, tax, or legal advice. Markets involve risk, and you should verify all information before making decisions.")
        Text(text = "Screenshots are used only to help identify the ticker and timeframe. Price analysis is calculated from configured market data, not from the screenshot image.")
    }
}
