from __future__ import annotations

import asyncio

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class RequestTimeoutMiddleware:
    """Enforces a maximum duration for HTTP requests."""

    def __init__(self, app: ASGIApp, timeout_seconds: float = 30.0) -> None:
        self.app = app
        self.timeout = timeout_seconds

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await asyncio.wait_for(self.app(scope, receive, send), timeout=self.timeout)
        except asyncio.TimeoutError:
            response = JSONResponse({"detail": "Request timed out"}, status_code=503)
            await response(scope, receive, send)
