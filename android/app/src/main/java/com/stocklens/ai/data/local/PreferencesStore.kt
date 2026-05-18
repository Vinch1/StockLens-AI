package com.stocklens.ai.data.local

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.stocklens.ai.data.model.UserSettings
import com.stocklens.ai.data.model.WatchlistItem
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.stockLensDataStore by preferencesDataStore(name = "stocklens_preferences")

class PreferencesStore(private val context: Context) {
    private object Keys {
        val onboardingComplete = booleanPreferencesKey("onboarding_complete")
        val apiBaseUrl = stringPreferencesKey("api_base_url")
        val dataMode = stringPreferencesKey("data_mode")
        val defaultTimeframe = stringPreferencesKey("default_timeframe")
        val defaultHorizon = stringPreferencesKey("default_horizon")
        val darkMode = booleanPreferencesKey("dark_mode")
        val watchlistSymbols = stringPreferencesKey("watchlist_symbols")
    }

    val settings: Flow<UserSettings> = context.stockLensDataStore.data.map { preferences ->
        UserSettings(
            onboardingComplete = preferences[Keys.onboardingComplete] ?: false,
            apiBaseUrl = preferences[Keys.apiBaseUrl] ?: "http://10.0.2.2:8000/",
            dataMode = preferences[Keys.dataMode] ?: "live",
            defaultTimeframe = preferences[Keys.defaultTimeframe] ?: "1D",
            defaultHorizon = preferences[Keys.defaultHorizon] ?: "swing",
            darkMode = preferences[Keys.darkMode] ?: false
        )
    }

    val watchlist: Flow<List<WatchlistItem>> = context.stockLensDataStore.data.map { preferences ->
        preferences[Keys.watchlistSymbols]
            .orEmpty()
            .split(",")
            .filter { it.isNotBlank() }
            .map { symbol -> WatchlistItem(symbol = symbol, companyName = symbol) }
    }

    suspend fun saveSettings(settings: UserSettings) {
        context.stockLensDataStore.edit { preferences ->
            preferences[Keys.onboardingComplete] = settings.onboardingComplete
            preferences[Keys.apiBaseUrl] = settings.apiBaseUrl
            preferences[Keys.dataMode] = settings.dataMode
            preferences[Keys.defaultTimeframe] = settings.defaultTimeframe
            preferences[Keys.defaultHorizon] = settings.defaultHorizon
            preferences[Keys.darkMode] = settings.darkMode
        }
    }

    suspend fun addWatchlistSymbol(symbol: String) {
        context.stockLensDataStore.edit { preferences ->
            val symbols = preferences[Keys.watchlistSymbols]
                .orEmpty()
                .split(",")
                .filter { it.isNotBlank() }
                .toMutableSet()
            symbols.add(symbol.uppercase())
            preferences[Keys.watchlistSymbols] = symbols.joinToString(",")
        }
    }

    suspend fun removeWatchlistSymbol(symbol: String) {
        context.stockLensDataStore.edit { preferences ->
            val symbols = preferences[Keys.watchlistSymbols]
                .orEmpty()
                .split(",")
                .filter { it.isNotBlank() && it != symbol.uppercase() }
            preferences[Keys.watchlistSymbols] = symbols.joinToString(",")
        }
    }
}
