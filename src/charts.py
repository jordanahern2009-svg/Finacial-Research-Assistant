"""Plotly chart builders used by the Streamlit UI."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def price_chart(history: pd.DataFrame, ticker: str) -> go.Figure:
    figure = go.Figure()
    if history.empty:
        figure.update_layout(title="No price history available")
        return figure

    figure.add_trace(
        go.Scatter(
            x=history.index,
            y=history["Close"],
            mode="lines",
            name="Close",
            line={"color": "#8b5cf6", "width": 3},
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.10)",
            hovertemplate="$%{y:,.2f}<extra></extra>",
        )
    )
    figure.update_layout(
        title=f"{ticker} price history",
        height=420,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        hovermode="x unified",
        template="plotly_dark",
        yaxis={"tickprefix": "$", "gridcolor": "rgba(255,255,255,0.08)"},
        xaxis={"gridcolor": "rgba(255,255,255,0.08)"},
        legend={"orientation": "h"},
    )
    return figure


def volume_chart(history: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    if history.empty or "Volume" not in history:
        return figure
    figure.add_trace(
        go.Bar(
            x=history.index,
            y=history["Volume"],
            marker_color="#14b8a6",
            name="Volume",
            hovertemplate="%{y:,.0f}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Trading volume",
        height=230,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        template="plotly_dark",
        yaxis={"tickformat": ",.2s", "gridcolor": "rgba(255,255,255,0.08)"},
        xaxis={"gridcolor": "rgba(255,255,255,0.08)"},
        showlegend=False,
    )
    return figure
