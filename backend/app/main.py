from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.gzip import GZipMiddleware

from app.api_logging import ApiLoggingMiddleware
from app.config import get_settings
from app.logging_config import configure_api_logging
from app.middleware.timeout import RequestTimeoutMiddleware
from app.models import AnalyzeRequest, ScreenshotParseRequest
from app.providers import Providers, create_providers
from app.providers.errors import ProviderError
from app.services.analysis_service import analyze_ticker
from app.services.screenshot_parser import parse_screenshot

VERSION = "0.1.0"

_limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    loop = asyncio.get_event_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=8))
    app.state.providers = create_providers(settings)
    app.state.settings = settings
    yield


def _get_providers(app: FastAPI) -> Providers:
    return app.state.providers


def create_app() -> FastAPI:
    configure_api_logging()
    settings = get_settings()
    application = FastAPI(
        title="StockLens AI API",
        description="Stock research and risk-analysis assistant.",
        version=VERSION,
        lifespan=lifespan,
    )
    application.state.providers = create_providers(settings)
    application.state.settings = settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(RequestTimeoutMiddleware, timeout_seconds=30.0)
    application.add_middleware(GZipMiddleware, minimum_size=500)
    application.add_middleware(ApiLoggingMiddleware)
    application.state.limiter = _limiter
    application.add_middleware(SlowAPIMiddleware)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "stocklens-ai-api", "version": VERSION}

    @application.post("/api/analyze")
    @_limiter.limit("10/minute")
    async def analyze(request: Request, body: AnalyzeRequest) -> dict[str, object]:
        providers = _get_providers(application)
        try:
            return (await analyze_ticker(
                body,
                market_provider=providers.market,
                news_provider=providers.news,
                fundamentals_provider=providers.fundamentals,
                explanation_provider=providers.explanation,
            )).model_dump()
        except ProviderError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/api/parse-screenshot")
    async def parse_screenshot_endpoint(request: ScreenshotParseRequest) -> dict[str, object]:
        providers = _get_providers(application)
        return (
            await parse_screenshot(
                image_base64=request.image_base64,
                filename=request.filename,
                chart_metadata_provider=providers.chart_vision,
            )
        ).model_dump()

    @application.get("/api/providers/status")
    def providers_status() -> dict[str, object]:
        providers = _get_providers(application)
        provider_list = [providers.market.status(), providers.news.status(), providers.fundamentals.status()]
        if providers.explanation:
            provider_list.append(providers.explanation.status())
        if providers.chart_vision:
            provider_list.append(providers.chart_vision.status())
        return {"status": "ok", "providers": provider_list}

    return application


app = create_app()
