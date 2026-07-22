"""Plotly chart construction, kept separate from the pages that display them.

All charts share a consistent, attractive color template so the app looks
cohesive regardless of which page is showing a chart.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEMPLATE = "plotly_white"
ACCENT_SEQUENCE = ["#6C5CE7", "#00B894", "#0984E3", "#E17055", "#FDCB6E", "#E84393"]


def histogram(df: pd.DataFrame, column: str) -> go.Figure:
    fig = px.histogram(
        df, x=column, template=TEMPLATE, color_discrete_sequence=ACCENT_SEQUENCE,
        title=f"Distribution of {column}",
    )
    _style(fig)
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, color: str | None = None) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, color=color, template=TEMPLATE,
        color_discrete_sequence=ACCENT_SEQUENCE, opacity=0.75,
        title=f"{y} vs {x}",
    )
    _style(fig)
    return fig


def category_bar(value_counts: dict[str, int], column: str) -> go.Figure:
    labels = list(value_counts.keys())
    values = list(value_counts.values())
    fig = px.bar(
        x=labels, y=values, template=TEMPLATE, color_discrete_sequence=ACCENT_SEQUENCE,
        title=f"Top values of {column}", labels={"x": column, "y": "count"},
    )
    _style(fig)
    return fig


def missing_values_bar(missing: dict[str, int]) -> go.Figure:
    non_zero = {k: v for k, v in missing.items() if v > 0}
    if not non_zero:
        return go.Figure()
    fig = px.bar(
        x=list(non_zero.keys()), y=list(non_zero.values()), template=TEMPLATE,
        color_discrete_sequence=ACCENT_SEQUENCE, title="Missing Values by Column",
        labels={"x": "column", "y": "missing count"},
    )
    _style(fig)
    return fig


def correlation_heatmap(corr: dict) -> go.Figure:
    if not corr:
        return go.Figure()
    cols = list(corr.keys())
    z = [[corr[c1].get(c2, 0) for c2 in cols] for c1 in cols]
    fig = go.Figure(
        data=go.Heatmap(z=z, x=cols, y=cols, colorscale="Purples", zmid=0)
    )
    fig.update_layout(template=TEMPLATE, title="Correlation Matrix")
    _style(fig)
    return fig


def _style(fig: go.Figure) -> None:
    fig.update_layout(
        font=dict(family="Inter, -apple-system, sans-serif", size=13),
        title_font=dict(size=16),
        margin=dict(l=30, r=30, t=60, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
