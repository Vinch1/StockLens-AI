package com.stocklens.ai.ui.navigation

import androidx.compose.animation.AnimatedContentTransitionScope
import androidx.compose.animation.core.tween
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
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
import com.stocklens.ai.ui.theme.Primary
import com.stocklens.ai.viewmodel.StockLensViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StockLensNavHost(viewModel: StockLensViewModel) {
    val navController = rememberNavController()
    val appUiState by viewModel.appUiState.collectAsState()
    val analyzeUiState by viewModel.analyzeUiState.collectAsState()
    val screenshotUiState by viewModel.screenshotUiState.collectAsState()
    val startDestination = if (appUiState.settings.onboardingComplete) Destination.Home.route else Destination.Onboarding.route

    if (appUiState.isLoading) {
        LoadingState()
        return
    }

    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination
    val showBottomBar = bottomBarDestinations.any { it.route == currentDestination?.route }

    val currentTitle = when (currentDestination?.route) {
        Destination.Home.route -> "StockLens AI"
        Destination.Analyze.route -> "Analyze"
        Destination.ScreenshotConfirm.route -> "Screenshot Input"
        Destination.Watchlist.route -> "Watchlist"
        Destination.Settings.route -> "Settings"
        Destination.Onboarding.route -> "Welcome"
        else -> null
    }

    Scaffold(
        containerColor = Color.Transparent,
        topBar = {
            if (currentTitle != null) {
                TopAppBar(
                    title = {
                        Text(
                            text = currentTitle,
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.Bold
                        )
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                        titleContentColor = MaterialTheme.colorScheme.onSurface,
                    )
                )
            }
        },
        bottomBar = {
            if (showBottomBar) {
                NavigationBar(
                    tonalElevation = 8.dp
                ) {
                    bottomBarDestinations.forEach { destination ->
                        val selected = currentDestination?.hierarchy?.any { it.route == destination.route } == true
                        NavigationBarItem(
                            selected = selected,
                            onClick = {
                                navController.navigate(destination.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        inclusive = true
                                    }
                                    launchSingleTop = true
                                }
                            },
                            icon = {
                                Icon(
                                    imageVector = destination.icon,
                                    contentDescription = destination.label
                                )
                            },
                            label = {
                                Text(
                                    text = destination.label,
                                    fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal
                                )
                            },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = Primary,
                                selectedTextColor = Primary,
                                indicatorColor = Primary.copy(alpha = 0.12f),
                                unselectedIconColor = androidx.compose.material3.MaterialTheme.colorScheme.onSurfaceVariant,
                                unselectedTextColor = androidx.compose.material3.MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = startDestination,
            enterTransition = { slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.Start, tween(300)) },
            exitTransition = { slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.Start, tween(300)) },
            popEnterTransition = { slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.End, tween(300)) },
            popExitTransition = { slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.End, tween(300)) },
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
                ScreenshotConfirmationScreen(
                    screenshotUiState = screenshotUiState,
                    paddingValues = paddingValues,
                    onImageSelected = viewModel::parseScreenshot,
                    onUseDetectedFields = {
                        viewModel.applyScreenshotDetectionToForm()
                        navController.popBackStack()
                    },
                    onDone = { navController.popBackStack() }
                )
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
                    onSave = viewModel::saveSettings,
                    onDarkModeChange = { darkMode ->
                        viewModel.saveSettings(appUiState.settings.copy(darkMode = darkMode))
                    }
                )
            }
        }
    }
}
