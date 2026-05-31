package com.stocklens.ai.data.remote

import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object NetworkModule {
    private const val DEFAULT_URL = "http://10.0.2.2:8000/"

    @Volatile
    var currentBaseUrl: String = DEFAULT_URL

    private val urlRewriteInterceptor = Interceptor { chain ->
        val original = chain.request()
        val base = currentBaseUrl.toHttpUrlOrNull()
        if (base != null) {
            val newUrl = original.url.newBuilder()
                .scheme(base.scheme)
                .host(base.host)
                .port(base.port)
                .build()
            chain.proceed(original.newBuilder().url(newUrl).build())
        } else {
            chain.proceed(original)
        }
    }

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(urlRewriteInterceptor)
        .addInterceptor(loggingInterceptor)
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    val api: StockLensApi = Retrofit.Builder()
        .baseUrl(DEFAULT_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(StockLensApi::class.java)
}
