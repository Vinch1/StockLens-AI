from __future__ import annotations

import asyncio

import yfinance as yf

from app.models import FundamentalMetrics, FundamentalsSummary
from app.providers.cache import _fundamentals_cache, aget_with_cache
from app.providers.errors import ProviderDataError


class YFinanceFundamentalsProvider:
    mode = "live"

    async def get_fundamentals(self, ticker: str) -> FundamentalsSummary:
        return await aget_with_cache(
            _fundamentals_cache,
            ("fundamentals", ticker),
            lambda: self._fetch(ticker),
        )

    async def _fetch(self, ticker: str) -> FundamentalsSummary:
        try:
            info: dict = await asyncio.to_thread(lambda: yf.Ticker(ticker).info) or {}
        except Exception as exc:
            raise ProviderDataError(str(exc)) from exc

        if not info:
            return FundamentalsSummary(
                quality="unavailable",
                score=0,
                metrics=FundamentalMetrics(),
                summary=f"Fundamental data for {ticker} is unavailable. Review fundamentals and valuation with a qualified professional.",
            )

        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        free_cash_flow = info.get("freeCashflow")
        debt_to_equity = info.get("debtToEquity")
        pe_ratio = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        gross_margin = info.get("grossMargins")
        operating_margin = info.get("operatingMargins")

        def _round(value: float | None) -> float | None:
            if value is None:
                return None
            return round(value, 4)

        metrics = FundamentalMetrics(
            revenue_growth=_round(revenue_growth),
            earnings_growth=_round(earnings_growth),
            free_cash_flow=_round(free_cash_flow),
            debt_to_equity=_round(debt_to_equity),
            pe_ratio=_round(pe_ratio),
            forward_pe=_round(forward_pe),
            gross_margin=_round(gross_margin),
            operating_margin=_round(operating_margin),
        )

        growth_score = 50

        if revenue_growth is not None:
            if revenue_growth > 0:
                growth_score += 15
            if revenue_growth > 0.15:
                growth_score += 10

        if earnings_growth is not None:
            if earnings_growth > 0:
                growth_score += 15
            if earnings_growth > 0.2:
                growth_score += 10

        cash_flow_score = 50
        if free_cash_flow is not None and free_cash_flow > 0:
            cash_flow_score += 30

        balance_sheet_score = 50

        if debt_to_equity is not None:
            if debt_to_equity < 100:
                balance_sheet_score += 15
            if debt_to_equity < 50:
                balance_sheet_score += 10
            if debt_to_equity > 200:
                balance_sheet_score -= 20

        valuation_score = 50
        if pe_ratio is not None:
            if 5 < pe_ratio < 35:
                valuation_score += 20
            if pe_ratio > 100:
                valuation_score -= 20

        profitability_score = 50
        if gross_margin is not None:
            if gross_margin > 0.3:
                profitability_score += 15
            if gross_margin > 0.5:
                profitability_score += 10

        if operating_margin is not None and operating_margin > 0.15:
            profitability_score += 15

        growth_score = max(0, min(100, growth_score))
        profitability_score = max(0, min(100, profitability_score))
        balance_sheet_score = max(0, min(100, balance_sheet_score))
        valuation_score = max(0, min(100, valuation_score))
        cash_flow_score = max(0, min(100, cash_flow_score))
        score = round(
            (growth_score * 0.25)
            + (profitability_score * 0.25)
            + (balance_sheet_score * 0.20)
            + (valuation_score * 0.15)
            + (cash_flow_score * 0.15)
        )

        if score >= 70:
            quality = "strong"
        elif score >= 45:
            quality = "average"
        elif score > 0:
            quality = "weak"
        else:
            quality = "unavailable"

        summary_parts: list[str] = [
            f"Fundamental analysis for {ticker}: quality={quality}, score={score}/100."
        ]

        if metrics.revenue_growth is not None:
            summary_parts.append(f"Revenue growth: {metrics.revenue_growth * 100:.2f}%.")

        if metrics.earnings_growth is not None:
            summary_parts.append(f"Earnings growth: {metrics.earnings_growth * 100:.2f}%.")

        if metrics.free_cash_flow is not None:
            summary_parts.append(f"Free cash flow: ${metrics.free_cash_flow:,.0f}.")

        if metrics.debt_to_equity is not None:
            summary_parts.append(f"Debt-to-equity: {metrics.debt_to_equity:.2f}.")

        if metrics.pe_ratio is not None:
            summary_parts.append(f"P/E ratio: {metrics.pe_ratio:.2f}.")

        if metrics.gross_margin is not None:
            summary_parts.append(f"Gross margin: {metrics.gross_margin * 100:.2f}%.")

        if metrics.operating_margin is not None:
            summary_parts.append(f"Operating margin: {metrics.operating_margin * 100:.2f}%.")

        summary_parts.append("Review fundamentals and valuation with a qualified professional.")

        return FundamentalsSummary(
            quality=quality,
            score=score,
            metrics=metrics,
            summary=" ".join(summary_parts),
            growth_score=growth_score,
            profitability_score=profitability_score,
            balance_sheet_score=balance_sheet_score,
            valuation_score=valuation_score,
            cash_flow_score=cash_flow_score,
        )

    def status(self) -> dict[str, object]:
        return {
            "name": "fundamentals",
            "mode": "live",
            "configured": True,
            "message": "Fetching live fundamentals from Yahoo Finance.",
        }
