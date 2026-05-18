package com.stocklens.ai.ui.screens.onboarding

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.stocklens.ai.ui.screens.ScreenScaffold

@Composable
fun OnboardingScreen(paddingValues: PaddingValues, onComplete: () -> Unit) {
    ScreenScaffold(title = "Welcome to StockLens AI", paddingValues = paddingValues) {
        Text(
            text = "StockLens AI helps you study technical setup, news catalysts, fundamentals, and risk factors.",
            style = MaterialTheme.typography.bodyLarge
        )
        Card {
            androidx.compose.foundation.layout.Column(
                modifier = Modifier.height(220.dp),
                verticalArrangement = Arrangement.Center
            ) {
                Text(text = "Important disclaimer", style = MaterialTheme.typography.titleMedium)
                Text(text = "StockLens AI provides educational research summaries only. It is not financial, investment, tax, or legal advice. Markets involve risk, and you should verify all information before making decisions.")
                Text(text = "The app does not place trades, connect brokerage accounts, or provide personalized recommendations.")
            }
        }
        Spacer(modifier = Modifier.weight(1f))
        Button(onClick = onComplete, modifier = Modifier.fillMaxWidth().height(56.dp)) {
            Text(text = "I understand — continue")
        }
    }
}
