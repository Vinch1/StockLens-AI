from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

_TERMINAL_MESSAGE_LIMIT = 50
_configured = False
_log_file_path: Path | None = None


def configure_api_logging(log_dir: Path | None = None, *, force: bool = False) -> Path:
    global _configured, _log_file_path

    if _configured and _log_file_path is not None and not force:
        return _log_file_path

    log_directory = log_dir or Path(__file__).resolve().parents[1] / "log"
    log_directory.mkdir(parents=True, exist_ok=True)
    _log_file_path = _daily_log_file_path(log_directory)

    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        colorize=True,
        format=_terminal_format,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        _log_file_path,
        level="INFO",
        encoding="utf-8",
        mode="a",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
        backtrace=False,
        diagnose=False,
    )

    _configured = True
    logger.info("API logger initialized log_file={}", _log_file_path)
    return _log_file_path


def _terminal_format(record: dict[str, Any]) -> str:
    record["extra"]["terminal_message"] = _truncate_terminal_message(record["message"])
    level_name = record["level"].name
    if level_name in {"ERROR", "CRITICAL"}:
        color = "red"
    elif level_name == "WARNING":
        color = "yellow"
    else:
        color = "white"
    return f"<{color}>{{time:YYYY-MM-DD HH:mm:ss}} | {{level:<8}} | {{extra[terminal_message]}}</{color}>\n"


def _truncate_terminal_message(message: str) -> str:
    return message[:_TERMINAL_MESSAGE_LIMIT]


def _daily_log_file_path(log_directory: Path) -> Path:
    return log_directory / f"{datetime.now().strftime('%Y-%m-%d')}.txt"
