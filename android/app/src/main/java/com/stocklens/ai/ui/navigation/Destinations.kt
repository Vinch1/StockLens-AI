package com.stocklens.ai.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Destination(val route: String, val label: String, val icon: ImageVector) {
    data object Onboarding : Destination("onboarding", "Onboarding", Icons.Default.Home)
    data object Home : Destination("home", "Home", Icons.Default.Home)
    data object Analyze : Destination("analyze", "Analyze", Icons.Default.Analytics)
    data object ScreenshotConfirm : Destination("screenshot_confirm", "Screenshot", Icons.Default.Visibility)
    data object Report : Destination("report", "Report", Icons.Default.Analytics)
    data object Watchlist : Destination("watchlist", "Watchlist", Icons.Default.Visibility)
    data object Settings : Destination("settings", "Settings", Icons.Default.Settings)
}

val bottomBarDestinations = listOf(
    Destination.Home,
    Destination.Analyze,
    Destination.Watchlist,
    Destination.Settings
)
