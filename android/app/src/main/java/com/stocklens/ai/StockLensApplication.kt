package com.stocklens.ai

import android.app.Application
import com.stocklens.ai.data.local.PreferencesStore
import com.stocklens.ai.data.remote.NetworkModule
import com.stocklens.ai.data.remote.NetworkMonitor
import com.stocklens.ai.data.repository.StockLensRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch

class StockLensApplication : Application() {
    val networkMonitor: NetworkMonitor by lazy { NetworkMonitor(applicationContext) }

    val repository: StockLensRepository by lazy {
        StockLensRepository(
            api = NetworkModule.api,
            preferencesStore = PreferencesStore(applicationContext)
        )
    }

    override fun onCreate() {
        super.onCreate()
        CoroutineScope(Dispatchers.IO).launch {
            repository.settings.firstOrNull()?.let {
                NetworkModule.currentBaseUrl = it.apiBaseUrl
            }
        }
    }
}
