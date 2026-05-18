package com.stocklens.ai.ui.navigation

sealed class Destination(val route: String, val label: String) {
    data object Onboarding : Destination("onboarding", "Onboarding")
    data object Home : Destination("home", "Home")
    data object Analyze : Destination("analyze", "Analyze")
    data object ScreenshotConfirm : Destination("screenshot_confirm", "Screenshot")
    data object Report : Destination("report", "Report")
    data object Watchlist : Destination("watchlist", "Watchlist")
    data object Settings : Destination("settings", "Settings")
}

val bottomBarDestinations = listOf(
    Destination.Home,
    Destination.Analyze,
    Destination.Watchlist,
    Destination.Settings
)
