package com.stocklens.ai.ui.screens.analyze

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import com.stocklens.ai.ui.screens.ScreenScaffold

@Composable
fun ScreenshotConfirmationScreen(paddingValues: PaddingValues, onDone: () -> Unit) {
    val ticker = remember { mutableStateOf("") }
    val timeframe = remember { mutableStateOf("1D") }
    ScreenScaffold(title = "Screenshot confirmation", paddingValues = paddingValues) {
        Text("Screenshots are used only to help identify the ticker and timeframe. Price analysis is calculated from configured market data, not from the screenshot image.")
        Text("OCR is a placeholder in this MVP. Confirm or edit the detected fields before analysis.")
        OutlinedTextField(value = ticker.value, onValueChange = { ticker.value = it.uppercase() }, label = { Text("Detected ticker") })
        OutlinedTextField(value = timeframe.value, onValueChange = { timeframe.value = it }, label = { Text("Detected timeframe") })
        Button(onClick = onDone) { Text("Confirm and return") }
    }
}
