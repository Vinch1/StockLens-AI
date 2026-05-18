package com.stocklens.ai.ui.navigation

import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.stocklens.ai.ui.screens.LoadingState
import com.stocklens.ai.ui.screens.analyze.AnalyzeScreen
import com.stocklens.ai.ui.screens.analyze.ScreenshotConfirmationScreen
import com.stocklens.ai.ui.screens.home.HomeScreen
import com.stocklens.ai.ui.screens.onboarding.OnboardingScreen
import com.stocklens.ai.ui.screens.report.ReportScreen
import com.stocklens.ai.ui.screens.settings.SettingsScreen
import com.stocklens.ai.ui.screens.watchlist.WatchlistScreen
import com.stocklens.ai.viewmodel.StockLensViewModel

@Composable
fun StockLensNavHost(viewModel: StockLensViewModel) {
    val navController = rememberNavController()
    val appUiState by viewModel.appUiState.collectAsState()
    val analyzeUiState by viewModel.analyzeUiState.collectAsState()
    val startDestination = if (appUiState.settings.onboardingComplete) Destination.Home.route else Destination.Onboarding.route

    if (appUiState.isLoading) {
        LoadingState()
        return
    }

    Scaffold(
        bottomBar = {
            val backStackEntry by navController.currentBackStackEntryAsState()
            val currentDestination = backStackEntry?.destination
            NavigationBar {
                bottomBarDestinations.forEach { destination ->
                    NavigationBarItem(
                        selected = currentDestination?.hierarchy?.any { it.route == destination.route } == true,
                        onClick = {
                            navController.navigate(destination.route) {
                                launchSingleTop = true
                                popUpTo(Destination.Home.route) { saveState = true }
                                restoreState = true
                            }
                        },
                        icon = { Text(destination.label.take(1)) },
                        label = { Text(destination.label) }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = startDestination
        ) {
            composable(Destination.Onboarding.route) {
                OnboardingScreen(paddingValues = paddingValues) {
                    viewModel.completeOnboarding()
                    navController.navigate(Destination.Home.route) { popUpTo(Destination.Onboarding.route) { inclusive = true } }
                }
            }
            composable(Destination.Home.route) {
                HomeScreen(
                    appUiState = appUiState,
                    paddingValues = paddingValues,
                    onAnalyze = { navController.navigate(Destination.Analyze.route) },
                    onWatchlist = { navController.navigate(Destination.Watchlist.route) }
                )
            }
            composable(Destination.Analyze.route) {
                AnalyzeScreen(
                    analyzeUiState = analyzeUiState,
                    paddingValues = paddingValues,
                    onTickerChange = { viewModel.updateAnalyzeForm(ticker = it) },
                    onAssetTypeChange = { viewModel.updateAnalyzeForm(assetType = it) },
                    onTimeframeChange = { viewModel.updateAnalyzeForm(timeframe = it) },
                    onHorizonChange = { viewModel.updateAnalyzeForm(horizon = it) },
                    onIncludeNewsChange = { viewModel.updateAnalyzeForm(includeNews = it) },
                    onIncludeFundamentalsChange = { viewModel.updateAnalyzeForm(includeFundamentals = it) },
                    onAnalyze = viewModel::analyze,
                    onScreenshotConfirm = { navController.navigate(Destination.ScreenshotConfirm.route) },
                    onReport = { navController.navigate(Destination.Report.route) }
                )
            }
            composable(Destination.ScreenshotConfirm.route) {
                ScreenshotConfirmationScreen(paddingValues = paddingValues) { navController.popBackStack() }
            }
            composable(Destination.Report.route) {
                ReportScreen(analyzeUiState = analyzeUiState, paddingValues = paddingValues)
            }
            composable(Destination.Watchlist.route) {
                WatchlistScreen(
                    appUiState = appUiState,
                    paddingValues = paddingValues,
                    onAdd = viewModel::addWatchlistSymbol,
                    onRemove = viewModel::removeWatchlistSymbol
                )
            }
            composable(Destination.Settings.route) {
                SettingsScreen(
                    settings = appUiState.settings,
                    paddingValues = paddingValues,
                    onSave = viewModel::saveSettings
                )
            }
        }
    }
}
