package com.stocklens.ai.data.remote

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import java.io.IOException
import java.net.SocketTimeoutException
import retrofit2.HttpException

suspend fun <T> retryWithBackoff(
    maxRetries: Int = 2,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 4000,
    block: suspend () -> T
): T {
    var currentDelay = initialDelayMs
    repeat(maxRetries) {
        try {
            return block()
        } catch (e: CancellationException) {
            throw e
        } catch (_: SocketTimeoutException) {
            // retryable
        } catch (_: IOException) {
            // retryable
        } catch (e: HttpException) {
            if (e.code() !in 500..599) throw e
        }
        delay(currentDelay)
        currentDelay = (currentDelay * 2).coerceAtMost(maxDelayMs)
    }
    return block()
}
