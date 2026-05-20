from __future__ import annotations

import logging

_SUPPRESSED_MESSAGES = (
    "could not pre-load bedrock-runtime response stream shape",
    "could not pre-load sagemaker-runtime response stream shape",
)


class _OptionalAwsDependencyFilter(logging.Filter):
    _stocklens_filter = True

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not any(suppressed in message for suppressed in _SUPPRESSED_MESSAGES)


def suppress_litellm_optional_dependency_warnings() -> None:
    logger = logging.getLogger("LiteLLM")
    if any(getattr(log_filter, "_stocklens_filter", False) for log_filter in logger.filters):
        return
    logger.addFilter(_OptionalAwsDependencyFilter())


def suppress_litellm_debug_info(litellm_module: object) -> None:
    setattr(litellm_module, "suppress_debug_info", True)
