package com.stocklens.ai

import android.app.Application
import com.stocklens.ai.data.local.PreferencesStore
import com.stocklens.ai.data.remote.NetworkModule
import com.stocklens.ai.data.repository.StockLensRepository

class StockLensApplication : Application() {
    val repository: StockLensRepository by lazy {
        StockLensRepository(
            api = NetworkModule.api,
            preferencesStore = PreferencesStore(applicationContext)
        )
    }
}
