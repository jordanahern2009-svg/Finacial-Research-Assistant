"""Market-data access and normalization.

The app intentionally keeps the provider-specific code in this module. That makes
it straightforward to replace yfinance with a paid market-data API later without
rewriting the Streamlit UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd
import yfinance as yf


@dataclass
class ResearchData:
    """All data needed to render one company research session."""

    ticker: str
    info: dict[str, Any]
    history: pd.DataFrame
    income_statement: pd.DataFrame
    balance_sheet: pd.DataFrame
    cash_flow: pd.DataFrame
    news: list[dict[str, Any]]
    fetched_at: datetime


def normalize_ticker(raw_ticker: str) -> str:
    """Return a clean uppercase ticker symbol."""

    return raw_ticker.strip().upper().replace("$", "")


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_frame(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy()
    return pd.DataFrame()


def _extract_news_item(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize both old and new yfinance news response shapes."""

    content = item.get("content", item)
    provider = content.get("provider", {}) if isinstance(content, dict) else {}
    thumbnail = content.get("thumbnail", {}) if isinstance(content, dict) else {}
    resolutions = thumbnail.get("resolutions", []) if isinstance(thumbnail, dict) else []
    image_url = resolutions[0].get("url") if resolutions and isinstance(resolutions[0], dict) else None

    published = content.get("pubDate", content.get("providerPublishTime", ""))
    if isinstance(published, (int, float)):
        published = datetime.fromtimestamp(published).isoformat()

    return {
        "title": content.get("title", "Untitled article"),
        "publisher": provider.get("displayName", content.get("publisher", "Unknown source")),
        "link": content.get("canonicalUrl", {}).get("url", content.get("link", ""))
        if isinstance(content.get("canonicalUrl", {}), dict)
        else content.get("link", ""),
        "published": published,
        "summary": content.get("summary", ""),
        "image_url": image_url,
    }


def normalize_news(raw_news: Any) -> list[dict[str, Any]]:
    """Convert provider news into a small UI-friendly schema."""

    if not isinstance(raw_news, list):
        return []
    return [_extract_news_item(item) for item in raw_news if isinstance(item, dict)]


def load_research_data(raw_ticker: str, period: str = "1y") -> ResearchData:
    """Fetch quote, history, statements, and news for a ticker."""

    ticker = normalize_ticker(raw_ticker)
    if not ticker:
        raise ValueError("Enter a ticker symbol, such as AAPL or MSFT.")

    security = yf.Ticker(ticker)

    # `info` is slower than `fast_info`, but supplies useful company metadata and
    # statement-related fields. A provider failure should not blank the whole app.
    try:
        info = _safe_dict(security.info)
    except Exception:
        info = {}

    try:
        history = _safe_frame(security.history(period=period, interval="1d", auto_adjust=False))
    except Exception as exc:
        raise RuntimeError(f"Could not load price history for {ticker}: {exc}") from exc

    try:
        income_statement = _safe_frame(security.income_stmt)
    except Exception:
        income_statement = pd.DataFrame()
    try:
        balance_sheet = _safe_frame(security.balance_sheet)
    except Exception:
        balance_sheet = pd.DataFrame()
    try:
        cash_flow = _safe_frame(security.cashflow)
    except Exception:
        cash_flow = pd.DataFrame()
    try:
        news = normalize_news(security.news)
    except Exception:
        news = []

    if history.empty and not info:
        raise RuntimeError(f"No data found for {ticker}. Check the ticker and try again.")

    return ResearchData(
        ticker=ticker,
        info=info,
        history=history,
        income_statement=income_statement,
        balance_sheet=balance_sheet,
        cash_flow=cash_flow,
        news=news,
        fetched_at=datetime.now(),
    )


def latest_price(data: ResearchData) -> float | None:
    """Get the most recent close, if available."""

    if data.history.empty or "Close" not in data.history:
        return None
    value = data.history["Close"].dropna()
    return float(value.iloc[-1]) if not value.empty else None


def day_change(data: ResearchData) -> tuple[float | None, float | None]:
    """Return latest absolute and percentage change."""

    if data.history.empty or "Close" not in data.history:
        return None, None
    close = data.history["Close"].dropna()
    if len(close) < 2:
        return None, None
    current = float(close.iloc[-1])
    previous = float(close.iloc[-2])
    absolute = current - previous
    percent = absolute / previous * 100 if previous else None
    return absolute, percent


def statement_for_display(statement: pd.DataFrame, max_rows: int = 35) -> pd.DataFrame:
    """Transpose a provider statement into a readable table."""

    if statement.empty:
        return statement
    display = statement.transpose().copy()
    display.index = [str(index).split(" ")[0] for index in display.index]
    display = display.head(max_rows)
    return display
