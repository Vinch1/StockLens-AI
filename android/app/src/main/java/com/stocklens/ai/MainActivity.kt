package com.stocklens.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import com.stocklens.ai.ui.navigation.StockLensNavHost
import com.stocklens.ai.ui.theme.StockLensTheme
import com.stocklens.ai.viewmodel.StockLensViewModel
import com.stocklens.ai.viewmodel.StockLensViewModelFactory

class MainActivity : ComponentActivity() {
    private val viewModel: StockLensViewModel by viewModels {
        StockLensViewModelFactory((application as StockLensApplication).repository)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val appUiState by viewModel.appUiState.collectAsState()
            StockLensTheme(darkTheme = appUiState.settings.darkMode) {
                StockLensNavHost(viewModel = viewModel)
            }
        }
    }
}
