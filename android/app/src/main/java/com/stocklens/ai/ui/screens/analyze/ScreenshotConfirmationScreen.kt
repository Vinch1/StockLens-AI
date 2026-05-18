package com.stocklens.ai.ui.screens.analyze

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.stocklens.ai.ui.screens.ScreenScaffold

@Composable
fun ScreenshotConfirmationScreen(paddingValues: PaddingValues, onDone: () -> Unit) {
    val ticker = remember { mutableStateOf("") }
    val timeframe = remember { mutableStateOf("1D") }

    ScreenScaffold(title = "Screenshot Input", paddingValues = paddingValues) {
        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer)
        ) {
            Text(
                text = "Screenshots help identify the ticker and timeframe. Price analysis uses configured market data, not the image itself.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onTertiaryContainer,
                modifier = Modifier.padding(16.dp)
            )
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Text(
                text = "OCR is a placeholder in this MVP. Confirm or edit the detected fields before analysis.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(16.dp)
            )
        }

        OutlinedTextField(
            value = ticker.value,
            onValueChange = { ticker.value = it.uppercase() },
            label = { Text("Detected ticker") },
            modifier = Modifier.fillMaxWidth()
        )

        OutlinedTextField(
            value = timeframe.value,
            onValueChange = { timeframe.value = it },
            label = { Text("Detected timeframe") },
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = onDone,
            modifier = Modifier.fillMaxWidth().height(52.dp),
            shape = MaterialTheme.shapes.large
        ) {
            Icon(Icons.Default.Check, null, modifier = Modifier.size(20.dp))
            Spacer(Modifier.width(8.dp))
            Text("Confirm and return", fontWeight = FontWeight.SemiBold)
        }
    }
}
