package com.stocklens.ai.data.remote

import com.stocklens.ai.data.model.AnalyzeRequest
import com.stocklens.ai.data.model.AnalyzeResponse
import retrofit2.http.Body
import retrofit2.http.POST

interface StockLensApi {
    @POST("api/analyze")
    suspend fun analyze(@Body request: AnalyzeRequest): AnalyzeResponse
}
