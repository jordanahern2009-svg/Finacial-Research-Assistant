from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.ai import ai_is_configured, answer_question, research_brief
from src.charts import price_chart, volume_chart
from src.data import (
    ResearchData,
    day_change,
    latest_price,
    load_research_data,
    statement_for_display,
)

load_dotenv()

st.set_page_config(
    page_title="SignalDesk | Financial Research Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #0b1020; color: #f4f7ff; }
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] { color: #f4f7ff; }
    [data-testid="stSidebar"] { background: #11182b; border-right: 1px solid #24304b; }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] label,
    [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"] { color: #e7ebf7 !important; opacity: 1 !important; }
    [data-testid="stCaptionContainer"] { color: #c7d0e6 !important; }
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    .hero { padding: 1.5rem 0 1rem 0; }
    .eyebrow { color: #a78bfa; font-size: .82rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .hero h1 { margin: .25rem 0 .4rem 0; font-size: 3rem; line-height: 1; }
    .hero p { color: #d7dff0; font-size: 1.1rem; max-width: 760px; }
    .card { background: #131c32; border: 1px solid #263452; border-radius: 16px; padding: 1rem 1.1rem; min-height: 112px; }
    .card-label { color: #c7d0e6; font-size: .82rem; text-transform: uppercase; letter-spacing: .08em; }
    .card-value { color: #f7f8ff; font-size: 1.55rem; font-weight: 700; margin-top: .5rem; }
    .muted { color: #c1cbe1; }
    .news-card { border-bottom: 1px solid #263452; padding: .85rem 0; }
    .news-card a { color: #f7f8ff; text-decoration: none; font-weight: 650; }
    .disclaimer { color: #aeb9d2; font-size: .78rem; padding-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: object, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        return f"${float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


def compact_number(value: object) -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    for suffix, divisor in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(number) >= divisor:
            return f"{number / divisor:,.1f}{suffix}"
    return f"{number:,.0f}"


def render_metric(label: str, value: str, detail: str = "") -> None:
    st.markdown(
        f'<div class="card"><div class="card-label">{label}</div>'
        f'<div class="card-value">{value}</div><div class="muted">{detail}</div></div>',
        unsafe_allow_html=True,
    )


def context_for_ai(data: ResearchData) -> str:
    price = latest_price(data)
    change, change_pct = day_change(data)
    info_subset = {
        key: data.info.get(key)
        for key in (
            "longName",
            "sector",
            "industry",
            "website",
            "marketCap",
            "trailingPE",
            "forwardPE",
            "beta",
            "dividendYield",
            "52WeekChange",
        )
        if data.info.get(key) is not None
    }

    def statement_preview(frame: pd.DataFrame) -> dict[str, dict[str, object]]:
        if frame.empty:
            return {}
        selected = frame.loc[frame.index.intersection(
            ["Total Revenue", "Net Income", "Operating Income", "Total Assets", "Total Liabilities Net Minority Interest", "Free Cash Flow"]
        )]
        return json.loads(selected.to_json()) if not selected.empty else {}

    return json.dumps(
        {
            "ticker": data.ticker,
            "as_of": data.fetched_at.isoformat(timespec="minutes"),
            "quote": {"price": price, "day_change": change, "day_change_percent": change_pct},
            "company": info_subset,
            "income_statement": statement_preview(data.income_statement),
            "balance_sheet": statement_preview(data.balance_sheet),
            "cash_flow": statement_preview(data.cash_flow),
            "news": data.news[:8],
        },
        default=str,
    )


@st.cache_data(ttl=300, show_spinner=False)
def cached_load(ticker: str, period: str) -> ResearchData:
    return load_research_data(ticker, period)


with st.sidebar:
    st.markdown("## SignalDesk")
    st.caption("A student-built financial research workspace")
    ticker = st.text_input("Ticker symbol", value=st.session_state.get("ticker", "AAPL"), max_chars=12)
    period = st.selectbox("Price history", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
    run = st.button("Research company", type="primary", use_container_width=True)
    st.divider()
    st.markdown("**What this app does**")
    st.caption("Pulls market data, statements, news, charts, and AI-assisted explanations into one place.")
    st.caption("Data refreshes every 5 minutes while the app is open.")

if run or "research_data" not in st.session_state:
    with st.spinner(f"Loading {ticker.upper()} research data…"):
        try:
            st.session_state.research_data = cached_load(ticker, period)
            st.session_state.ticker = ticker.upper().strip().replace("$", "")
        except Exception as exc:
            st.error(str(exc))
            st.stop()

data: ResearchData = st.session_state.research_data
price = latest_price(data)
change, change_pct = day_change(data)
company_name = data.info.get("longName", data.ticker)

st.markdown(
    f'<div class="hero"><div class="eyebrow">Financial research assistant</div>'
    f'<h1>{company_name} <span class="muted">({data.ticker})</span></h1>'
    f'<p>Explore the numbers, understand the story, and ask better questions about {data.ticker}.</p></div>',
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
with metric_cols[0]:
    render_metric("Last price", money(price), f"As of {data.fetched_at.strftime('%b %d, %Y %I:%M %p')}")
with metric_cols[1]:
    change_text = f"{change:+,.2f}" if change is not None else "—"
    pct_text = f"{change_pct:+.2f}%" if change_pct is not None else ""
    render_metric("Daily move", change_text, pct_text)
with metric_cols[2]:
    render_metric("Market cap", compact_number(data.info.get("marketCap")), "Approximate")
with metric_cols[3]:
    render_metric("Sector", str(data.info.get("sector", "Unknown")), str(data.info.get("industry", "")))

tabs = st.tabs(["Overview", "Financials", "News & AI", "Ask the assistant"])

with tabs[0]:
    chart_col, about_col = st.columns([1.6, 1])
    with chart_col:
        st.plotly_chart(price_chart(data.history, data.ticker), use_container_width=True)
        st.plotly_chart(volume_chart(data.history), use_container_width=True)
    with about_col:
        st.subheader("Company snapshot")
        description = data.info.get("longBusinessSummary", "Company description was not returned by the data provider.")
        st.write(description)
        website = data.info.get("website")
        if website:
            st.link_button("Open company website", website)
        st.subheader("Key indicators")
        indicator_rows = {
            "Trailing P/E": data.info.get("trailingPE"),
            "Forward P/E": data.info.get("forwardPE"),
            "Beta": data.info.get("beta"),
            "Dividend yield": data.info.get("dividendYield"),
            "52-week change": data.info.get("52WeekChange"),
        }
        st.dataframe(pd.DataFrame.from_dict(indicator_rows, orient="index", columns=["Value"]), use_container_width=True)

with tabs[1]:
    st.subheader("Reported financial statements")
    statement_choice = st.radio("Statement", ["Income statement", "Balance sheet", "Cash flow"], horizontal=True)
    selected_statement = {
        "Income statement": data.income_statement,
        "Balance sheet": data.balance_sheet,
        "Cash flow": data.cash_flow,
    }[statement_choice]
    display_statement = statement_for_display(selected_statement)
    if display_statement.empty:
        st.info("This provider did not return a statement for the selected company.")
    else:
        st.dataframe(display_statement, use_container_width=True, height=620)
    st.caption("Statement values are provider-reported and may be restated. Confirm important figures in company filings.")

with tabs[2]:
    st.subheader("Recent company news")
    if not data.news:
        st.info("No recent news was returned for this ticker.")
    for item in data.news:
        title = item.get("title", "Untitled article")
        link = item.get("link")
        title_html = f'<a href="{link}" target="_blank">{title}</a>' if link else title
        st.markdown(
            f'<div class="news-card">{title_html}<br><span class="muted">{item.get("publisher", "Unknown source")} · {item.get("published", "")}</span>'
            f'<br>{item.get("summary", "")}</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("AI research brief")
    if not ai_is_configured():
        st.info("Add LLM_API_KEY to .env to enable AI summaries and company Q&A. The rest of the app works without it.")
    elif st.button("Generate research brief", type="primary"):
        with st.spinner("Reading the current research context…"):
            try:
                st.markdown(research_brief(context_for_ai(data)))
            except Exception as exc:
                st.error(f"AI request failed: {exc}")

with tabs[3]:
    st.subheader("Ask about this company")
    st.caption("Questions are answered from the current ticker data and recent news.")
    if not ai_is_configured():
        st.info("Add LLM_API_KEY to .env to enable questions.")
    else:
        question = st.text_area(
            "Your question",
            placeholder="What changed in the latest reported revenue, and what should I investigate next?",
            height=110,
        )
        if st.button("Ask", type="primary"):
            if not question.strip():
                st.warning("Write a question first.")
            else:
                with st.spinner("Analyzing the current research context…"):
                    try:
                        st.markdown(answer_question(context_for_ai(data), question.strip()))
                    except Exception as exc:
                        st.error(f"AI request failed: {exc}")

st.markdown(
    "<div class='disclaimer'>Educational project for exploring public market data. Not financial advice. "
    "Data can be delayed, incomplete, or inaccurate; verify important claims with primary filings.</div>",
    unsafe_allow_html=True,
)
