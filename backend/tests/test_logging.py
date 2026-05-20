from __future__ import annotations

from datetime import datetime

from loguru import logger

from app.api_logging import _decode_bytes, _level_for_status
from app.logging_config import _truncate_terminal_message, configure_api_logging
from app.models import NewsItem, NewsSummary
from app.services.analysis_service import _log_collected_news


def test_terminal_messages_are_truncated_to_first_50_characters():
    assert _truncate_terminal_message("x" * 80) == "x" * 50


def test_api_status_levels_map_to_expected_terminal_colors():
    assert _level_for_status(200) == "INFO"
    assert _level_for_status(404) == "WARNING"
    assert _level_for_status(500) == "ERROR"


def test_decode_bytes_preserves_full_log_content():
    assert _decode_bytes(("a" * 80).encode()) == "a" * 80


def test_api_logging_uses_current_date_file_and_appends(tmp_path):
    path = configure_api_logging(tmp_path, force=True)
    assert path == tmp_path / f"{datetime.now().strftime('%Y-%m-%d')}.txt"

    logger.info("first daily log entry")
    first_size = path.stat().st_size
    path_again = configure_api_logging(tmp_path, force=True)
    logger.info("second daily log entry")

    assert path_again == path
    text = path.read_text(encoding="utf-8")
    assert path.stat().st_size > first_size
    assert "first daily log entry" in text
    assert "second daily log entry" in text


def test_api_logging_keeps_full_message_for_file_sinks(client):
    messages: list[str] = []
    sink_id = logger.add(messages.append, level="INFO", format="{message}")
    long_content = "x" * 80

    try:
        response = client.post("/api/parse-screenshot", json={"image_base64": long_content})
    finally:
        logger.remove(sink_id)

    assert response.status_code == 200
    assert any(long_content in message for message in messages)


def test_collected_news_logging_includes_full_news_payload():
    messages: list[str] = []
    sink_id = logger.add(messages.append, level="INFO", format="{message}")
    long_title = "AAPL wins major enterprise AI deal with very long detailed headline"

    try:
        _log_collected_news(
            "AAPL",
            NewsSummary(
                sentiment="positive",
                score=20,
                summary="Recent news for AAPL shows positive sentiment.",
                items=[
                    NewsItem(
                        title=long_title,
                        source="Example News",
                        published_at="2026-05-20T00:00:00+00:00",
                        url="https://example.com/aapl-ai-deal",
                        sentiment="positive",
                        catalyst_type="product",
                        summary="AAPL announced a large enterprise AI partnership.",
                    )
                ],
            ),
        )
    finally:
        logger.remove(sink_id)

    assert any("Collected news" in message for message in messages)
    assert any(long_title in message for message in messages)
    assert any("https://example.com/aapl-ai-deal" in message for message in messages)
