from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import DEFAULT_THRESHOLDS

CHART_LABELS = {
    "avg_score": "Durchschnitt",
    "kompetenzfeld": "Kompetenzfeld",
    "unterkategorie": "Unterkategorie",
    "bus_factor": "Bus-Faktor",
    "weak_share": "Anteil schwacher Bewertungen",
    "expert_count": "Anzahl Expert:innen",
    "no_expert": "Ohne Expert:innen",
    "bottleneck": "Flaschenhals",
}


def _style_figure(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=16, r=16, t=56, b=16),
        coloraxis_colorbar_title="Bewertung",
    )
    return fig


def create_ranked_bar_chart(
    summary_df: pd.DataFrame,
    *,
    category_col: str,
    value_col: str,
    title: str,
    ascending: bool,
    limit: int = 8,
) -> go.Figure:
    if summary_df.empty:
        return _style_figure(go.Figure(), title)

    data = summary_df.sort_values(value_col, ascending=ascending).head(limit).copy()
    fig = px.bar(
        data,
        x=value_col,
        y=category_col,
        orientation="h",
        color=value_col,
        color_continuous_scale="RdYlGn",
        range_color=(DEFAULT_THRESHOLDS.min_score, DEFAULT_THRESHOLDS.max_score),
        text=value_col,
        labels=CHART_LABELS,
    )
    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        hovertemplate=(
            f"{CHART_LABELS.get(category_col, category_col)}: "
            "%{y}<br>Durchschnitt: %{x:.2f}<extra></extra>"
        ),
    )
    fig.update_yaxes(categoryorder="total ascending")
    return _style_figure(fig, title)


def create_risk_scatter(summary_df: pd.DataFrame, title: str) -> go.Figure:
    if summary_df.empty:
        return _style_figure(go.Figure(), title)

    display_df = summary_df.copy()
    display_df["no_expert"] = display_df["no_expert"].map({True: "Ja", False: "Nein"})
    display_df["bottleneck"] = display_df["bottleneck"].map({True: "Ja", False: "Nein"})

    fig = px.scatter(
        display_df,
        x="avg_score",
        y="bus_factor",
        color="no_expert",
        symbol="bottleneck",
        size="weak_share",
        custom_data=["unterkategorie", "expert_count", "weak_share", "no_expert", "bottleneck"],
        color_discrete_map={"Ja": "#c0392b", "Nein": "#1f77b4"},
        labels=CHART_LABELS,
    )
    fig.update_traces(
        hovertemplate=(
            "Unterkategorie: %{customdata[0]}<br>"
            "Durchschnitt: %{x:.2f}<br>"
            "Bus-Faktor: %{y}<br>"
            "Anzahl Expert:innen: %{customdata[1]}<br>"
            "Anteil schwacher Bewertungen: %{customdata[2]:.2%}<br>"
            "Ohne Expert:innen: %{customdata[3]}<br>"
            "Flaschenhals: %{customdata[4]}<extra></extra>"
        )
    )
    fig.update_layout(
        legend_title_text="Ohne Expert:innen",
    )
    fig.update_xaxes(
        range=[DEFAULT_THRESHOLDS.min_score - 0.1, DEFAULT_THRESHOLDS.max_score + 0.1],
        title_text="Durchschnitt",
    )
    fig.update_yaxes(dtick=1, rangemode="tozero")
    return _style_figure(fig, title)


def create_heatmap(heatmap_df: pd.DataFrame, title: str) -> go.Figure:
    if heatmap_df.empty:
        return _style_figure(go.Figure(), title)

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=heatmap_df.values,
                x=list(heatmap_df.columns),
                y=list(heatmap_df.index),
                zmin=DEFAULT_THRESHOLDS.min_score,
                zmax=DEFAULT_THRESHOLDS.max_score,
                colorscale=[
                    [0.0, "#c0392b"],
                    [0.5, "#f4d03f"],
                    [1.0, "#1e8449"],
                ],
                colorbar=dict(title="Bewertung"),
                hovertemplate=(
                    "Unterkategorie: %{y}<br>Mitarbeitende: %{x}<br>"
                    "Durchschnitt: %{z:.2f}<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(height=max(420, len(heatmap_df.index) * 28))
    fig.update_xaxes(title_text="Mitarbeitende")
    fig.update_yaxes(title_text="Unterkategorie")
    return _style_figure(fig, title)


def create_employee_bar_chart(
    profile_df: pd.DataFrame,
    *,
    employee: str,
    title: str,
) -> go.Figure:
    if profile_df.empty:
        return _style_figure(go.Figure(), title)

    fig = px.bar(
        profile_df.sort_values("avg_score", ascending=True),
        x="avg_score",
        y="kompetenzfeld",
        orientation="h",
        color="avg_score",
        color_continuous_scale="RdYlGn",
        range_color=(DEFAULT_THRESHOLDS.min_score, DEFAULT_THRESHOLDS.max_score),
        text="avg_score",
        labels=CHART_LABELS,
    )
    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        hovertemplate="Kompetenzfeld: %{y}<br>Durchschnitt: %{x:.2f}<extra></extra>",
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text=f"Durchschnittsscore für {employee}")
    fig.update_yaxes(title_text="Kompetenzfeld")
    return _style_figure(fig, title)
