from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture
def live_wiring_client():
    """TestClient with MOCK_MODE=false but mock provider instances — tests DI wiring without real API calls."""
    from app.config import Settings

    settings = Settings(MOCK_MODE=False, MARKET_DATA_PROVIDER="mock", NEWS_PROVIDER="mock", FUNDAMENTALS_PROVIDER="mock")
    from app.providers import create_providers

    app = create_app()
    app.state.providers = create_providers(settings)
    return TestClient(app)
