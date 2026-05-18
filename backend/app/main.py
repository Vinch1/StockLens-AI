from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import AnalyzeRequest, ScreenshotParseRequest
from app.providers import Providers, create_providers
from app.providers.errors import ProviderError
from app.services.analysis_service import analyze_ticker
from app.services.screenshot_parser import parse_screenshot

VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    app.state.providers = create_providers(settings)
    app.state.settings = settings
    yield


def _get_providers(app: FastAPI) -> Providers:
    return app.state.providers


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="StockLens AI API",
        description="Educational stock research and risk-analysis assistant. Not financial advice.",
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

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "stocklens-ai-api", "version": VERSION}

    @application.post("/api/analyze")
    async def analyze(request: AnalyzeRequest) -> dict[str, object]:
        providers = _get_providers(application)
        try:
            return (await analyze_ticker(
                request,
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
        return await parse_screenshot(image_base64=request.image_base64, filename=request.filename)

    @application.get("/api/providers/status")
    def providers_status() -> dict[str, object]:
        providers = _get_providers(application)
        provider_list = [providers.market.status(), providers.news.status(), providers.fundamentals.status()]
        if providers.explanation:
            provider_list.append(providers.explanation.status())
        return {"status": "ok", "providers": provider_list}

    return application


app = create_app()
