from __future__ import annotations


class ProviderError(Exception):
    """Base error for all provider failures."""


class ProviderUnavailableError(ProviderError):
    """Network timeout or connection failure."""


class ProviderRateLimitError(ProviderError):
    """API rate limit exceeded (HTTP 429)."""


class ProviderDataError(ProviderError):
    """Malformed response or ticker not found."""
