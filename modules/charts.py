"""
Plotly Corporate Visualizations Module:
Implements clean, executive-grade charts with strict corporate color semantics:
- Green (#16A36A): >= 100% Achievement
- Orange (#F59E0B): 80% - 99.9% Achievement
- Red (#DC3545): < 80% Achievement
- Navy (#142B4A) & Teal (#00A6A6): Target vs Actual & General Indicators
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import COLORS, PRODUCT_COLORS, MONTHS_ORDER, THRESHOLD_GREEN, THRESHOLD_ORANGE


def _base_layout(fig: go.Figure, title: str, height: int = 380) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=COLORS["navy"], family="Cairo, Inter, sans-serif")),
        paper_bgcolor=COLORS["white"],
        plot_bgcolor=COLORS["white"],
        font=dict(color=COLORS["text"], family="Cairo, Inter, sans-serif", size=12),
        height=height,
        margin=dict(l=24, r=24, t=52, b=36),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor=COLORS["border"])
    fig.update_yaxes(gridcolor="#EEF2F6", zerolinecolor=COLORS["border"])
    return fig


def _achievement_color(pct: float) -> str:
    if pd.isna(pct):
        return COLORS["muted"]
    if pct >= THRESHOLD_GREEN:
        return COLORS["green"]
    if pct >= THRESHOLD_ORANGE:
        return COLORS["orange"]
    return COLORS["red"]


def chart_target_vs_actual(monthly_sum: pd.DataFrame, t: dict) -> go.Figure:
    df = monthly_sum.copy()
    df["Period_Label"] = df["Month"] + " " + df["Year"].astype(str)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Period_Label"],
            y=df["Target"],
            name=t["target"],
            marker_color=COLORS["navy"],
            opacity=0.88,
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Period_Label"],
            y=df["Actual"],
            name=t["actual"],
            marker_color=COLORS["teal"],
        )
    )
    fig.update_layout(barmode="group", bargap=0.22, bargroupgap=0.08)
    return _base_layout(fig, t["chart_tva"])


def chart_monthly_trend(monthly_sum: pd.DataFrame, t: dict) -> go.Figure:
    df = monthly_sum.copy()
    df["Period_Label"] = df["Month"] + " " + df["Year"].astype(str)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Period_Label"],
            y=df["Target"],
            name=t["target"],
            mode="lines+markers",
            line=dict(color=COLORS["navy"], width=2.5, dash="dash"),
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Period_Label"],
            y=df["Actual"],
            name=t["actual"],
            mode="lines+markers",
            line=dict(color=COLORS["teal"], width=3),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(0, 166, 166, 0.08)",
        )
    )
    return _base_layout(fig, t["chart_trend"])


def chart_achievement_pct(monthly_sum: pd.DataFrame, t: dict) -> go.Figure:
    df = monthly_sum.dropna(subset=["Achievement_Pct"]).copy()
    df["Period_Label"] = df["Month"] + " " + df["Year"].astype(str)
    bar_colors = [_achievement_color(v) for v in df["Achievement_Pct"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Period_Label"],
            y=df["Achievement_Pct"],
            name=t["achievement"],
            marker_color=bar_colors,
            text=[f"{v:.1f}%" for v in df["Achievement_Pct"]],
            textposition="outside",
        )
    )
    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color=COLORS["navy"],
        annotation_text="100% Target",
        annotation_position="top left",
    )
    return _base_layout(fig, t["chart_ach"])


def chart_product_performance(product_sum: pd.DataFrame, t: dict) -> go.Figure:
    df = product_sum.copy()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Product"],
            y=df["Target"],
            name=t["target"],
            marker_color=COLORS["navy"],
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Product"],
            y=df["Actual"],
            name=t["actual"],
            marker_color=COLORS["teal"],
        )
    )
    fig.update_layout(barmode="group", bargap=0.28)
    return _base_layout(fig, t["chart_prod"])


def chart_annual_comparison(annual_sum: pd.DataFrame, t: dict) -> go.Figure:
    df = annual_sum.copy()
    df["Year_Str"] = df["Year"].astype(str)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Year_Str"],
            y=df["Target"],
            name=t["target"],
            marker_color=COLORS["navy"],
            text=[f"{v:,.2f}" for v in df["Target"]],
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Year_Str"],
            y=df["Actual"],
            name=t["actual"],
            marker_color=COLORS["teal"],
            text=[f"{v:,.2f}" for v in df["Actual"]],
            textposition="auto",
        )
    )
    fig.update_layout(barmode="group", bargap=0.32)
    return _base_layout(fig, t["chart_annual"])


def chart_yoy_monthly(monthly_sum: pd.DataFrame, t: dict) -> go.Figure:
    df = monthly_sum.copy()
    year_palette = [COLORS["muted"], COLORS["navy"], COLORS["teal"], COLORS["green"]]
    years = sorted(df["Year"].unique())

    fig = go.Figure()
    for idx, yr in enumerate(years):
        sub = df[df["Year"] == yr].set_index("Month").reindex(MONTHS_ORDER).reset_index()
        fig.add_trace(
            go.Scatter(
                x=sub["Month"],
                y=sub["Actual"],
                name=f"{t['actual']} {yr}",
                mode="lines+markers",
                line=dict(color=year_palette[idx % len(year_palette)], width=2.8),
                marker=dict(size=6),
            )
        )
    return _base_layout(fig, t["chart_yoy_month"])


def chart_period_comparison(period_df: pd.DataFrame, period_col: str, title: str, t: dict) -> go.Figure:
    df = period_df.copy()
    df["Label"] = df["Year"].astype(str) + " - " + df[period_col]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Label"],
            y=df["Target"],
            name=t["target"],
            marker_color=COLORS["navy"],
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Label"],
            y=df["Actual"],
            name=t["actual"],
            marker_color=COLORS["teal"],
        )
    )
    fig.update_layout(barmode="group", bargap=0.25)
    return _base_layout(fig, title)
