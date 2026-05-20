from __future__ import annotations

from time import perf_counter
from typing import Any, Awaitable, Callable

from loguru import logger

ASGIReceive = Callable[[], Awaitable[dict[str, Any]]]
ASGISend = Callable[[dict[str, Any]], Awaitable[None]]
ASGIApp = Callable[[dict[str, Any], ASGIReceive, ASGISend], Awaitable[None]]


class ApiLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: ASGIReceive,
        send: ASGISend,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "")
        path = scope.get("path", "")
        query_string = _decode_bytes(scope.get("query_string", b""))
        request_chunks: list[bytes] = []
        response_chunks: list[bytes] = []
        status_code = 500
        started_at = perf_counter()

        async def receive_wrapper() -> dict[str, Any]:
            message = await receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if body:
                    request_chunks.append(body)
            return message

        async def send_wrapper(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    response_chunks.append(body)
            await send(message)

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        except Exception as exc:
            duration_ms = (perf_counter() - started_at) * 1000
            logger.opt(exception=exc).error(
                "API service error method={} path={} query={} duration_ms={:.2f} request_body={}",
                method,
                path,
                query_string or "<empty>",
                duration_ms,
                _decode_bytes(b"".join(request_chunks)),
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        logger.log(
            _level_for_status(status_code),
            "API service method={} path={} query={} status={} duration_ms={:.2f} request_body={} response_body={}",
            method,
            path,
            query_string or "<empty>",
            status_code,
            duration_ms,
            _decode_bytes(b"".join(request_chunks)),
            _decode_bytes(b"".join(response_chunks)),
        )


def _level_for_status(status_code: int) -> str:
    if status_code >= 500:
        return "ERROR"
    if status_code >= 400:
        return "WARNING"
    return "INFO"


def _decode_bytes(value: bytes) -> str:
    if not value:
        return "<empty>"
    return value.decode("utf-8", errors="replace")
