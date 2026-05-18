from __future__ import annotations

from app.models import TechnicalAnalysis
from app.providers.protocols import ExplanationProvider
from app.services.compliance import sanitize_or_fallback


def educational_conclusion(technical: TechnicalAnalysis, overall_score: int, confidence: str) -> str:
    if overall_score >= 70:
        label = "constructive research candidate"
    elif overall_score >= 55:
        label = "mixed research candidate"
    elif overall_score >= 40:
        label = "needs more confirmation"
    else:
        label = "high-risk setup"
    conclusion = (
        f"This is a {label}. The technical setup is {technical.setup.replace('_', ' ')}, "
        f"with {confidence} confidence based on configured data. Review risk factors, news context, "
        "and fundamentals before drawing educational conclusions; this is not a recommendation."
    )
    fallback = "This research summary is educational only and should be verified with a qualified professional."
    return sanitize_or_fallback(conclusion, fallback)


def get_educational_conclusion(
    technical: TechnicalAnalysis,
    overall_score: int,
    confidence: str,
    explanation_provider: ExplanationProvider | None = None,
    news_summary: str = "",
    fundamentals_summary: str = "",
) -> str:
    fallback = educational_conclusion(technical, overall_score, confidence)

    if explanation_provider is not None and explanation_provider.mode == "live":
        try:
            text = explanation_provider.generate_conclusion(
                setup=technical.setup,
                score=overall_score,
                confidence=confidence,
                news_summary=news_summary,
                fundamentals_summary=fundamentals_summary,
            )
            return sanitize_or_fallback(text, fallback)
        except Exception:
            return fallback

    return fallback
