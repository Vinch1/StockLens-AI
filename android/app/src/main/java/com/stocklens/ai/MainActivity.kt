package com.stocklens.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.core.view.WindowCompat
import com.stocklens.ai.ui.navigation.StockLensNavHost
import com.stocklens.ai.ui.theme.StockLensTheme
import com.stocklens.ai.viewmodel.StockLensViewModel
import com.stocklens.ai.viewmodel.StockLensViewModelFactory

class MainActivity : ComponentActivity() {
    private val viewModel: StockLensViewModel by viewModels {
        val app = application as StockLensApplication
        StockLensViewModelFactory(app.repository, app.networkMonitor)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val appUiState by viewModel.appUiState.collectAsState()
            val isDark = appUiState.settings.darkMode

            // Update system bar appearance to match theme
            val insetsController = WindowCompat.getInsetsController(window, window.decorView)
            insetsController.isAppearanceLightStatusBars = !isDark
            insetsController.isAppearanceLightNavigationBars = !isDark

            StockLensTheme(darkTheme = isDark) {
                StockLensNavHost(viewModel = viewModel)
            }
        }
    }
}
