import pandas as pd

from src.data import normalize_news, normalize_ticker, statement_for_display


def test_normalize_ticker():
    assert normalize_ticker("  $aapl ") == "AAPL"


def test_normalize_news_handles_new_shape():
    items = normalize_news(
        [
            {
                "content": {
                    "title": "Earnings update",
                    "pubDate": "2026-07-29T12:00:00Z",
                    "provider": {"displayName": "Example News"},
                    "canonicalUrl": {"url": "https://example.com/article"},
                }
            }
        ]
    )
    assert items[0]["title"] == "Earnings update"
    assert items[0]["publisher"] == "Example News"
    assert items[0]["link"] == "https://example.com/article"


def test_statement_for_display_transposes_periods():
    statement = pd.DataFrame(
        {pd.Timestamp("2025-12-31"): [100], pd.Timestamp("2024-12-31"): [80]},
        index=["Total Revenue"],
    )
    result = statement_for_display(statement)
    assert list(result.index) == ["2025-12-31", "2024-12-31"]
    assert result.iloc[0, 0] == 100
