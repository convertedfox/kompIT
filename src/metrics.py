from __future__ import annotations

import pandas as pd

from src.config import ThresholdConfig


def _group_summary(
    df_long: pd.DataFrame,
    group_columns: list[str],
    thresholds: ThresholdConfig,
) -> pd.DataFrame:
    aggregate = (
        df_long.groupby(group_columns, dropna=False)
        .agg(
            avg_score=("score", "mean"),
            median_score=("score", "median"),
            score_std=("score", "std"),
            weak_share=("is_weak", "mean"),
            response_count=("score", "size"),
            statement_count=("aussage", "nunique"),
            employee_count=("mitarbeiter", "nunique"),
        )
        .reset_index()
    )

    per_employee = (
        df_long.groupby([*group_columns, "mitarbeiter"], dropna=False)
        .agg(employee_avg=("score", "mean"))
        .reset_index()
    )
    redundancy = (
        per_employee.groupby(group_columns, dropna=False)
        .agg(
            bus_factor=(
                "employee_avg",
                lambda values: int((values >= thresholds.expert_threshold).sum()),
            ),
            expert_count=(
                "employee_avg",
                lambda values: int((values >= thresholds.expert_threshold).sum()),
            ),
        )
        .reset_index()
    )

    summary = aggregate.merge(redundancy, on=group_columns, how="left")
    summary["score_std"] = summary["score_std"].fillna(0.0)
    summary["bottleneck"] = summary["bus_factor"] == 1
    summary["no_expert"] = summary["bus_factor"] == 0
    summary["coverage_ratio"] = summary["bus_factor"] / summary["employee_count"].where(
        summary["employee_count"] > 0, 1
    )
    return summary


def get_overview_metrics(
    df_long: pd.DataFrame,
    thresholds: ThresholdConfig,
) -> dict[str, int | float]:
    subcategory_summary = get_subcategory_summary(df_long, thresholds)
    coverage_index = 0.0
    if not subcategory_summary.empty:
        coverage_index = float(
            (subcategory_summary["bus_factor"] >= thresholds.target_redundancy).mean()
        )
    return {
        "field_count": int(df_long["kompetenzfeld"].nunique()),
        "subcategory_count": int(df_long["unterkategorie"].nunique()),
        "statement_count": int(df_long["aussage"].nunique()),
        "employee_count": int(df_long["mitarbeiter"].nunique()),
        "overall_avg": float(df_long["score"].mean()),
        "skill_coverage_index": coverage_index,
        "bottleneck_count": int(subcategory_summary["bottleneck"].sum()),
        "no_expert_count": int(subcategory_summary["no_expert"].sum()),
    }


def get_field_summary(df_long: pd.DataFrame, thresholds: ThresholdConfig) -> pd.DataFrame:
    summary = _group_summary(df_long, ["kompetenzfeld"], thresholds)
    return summary.sort_values(["avg_score", "kompetenzfeld"], ascending=[False, True]).reset_index(
        drop=True
    )


def get_subcategory_summary(df_long: pd.DataFrame, thresholds: ThresholdConfig) -> pd.DataFrame:
    summary = _group_summary(df_long, ["kompetenzfeld", "unterkategorie"], thresholds)
    return summary.sort_values(["avg_score", "unterkategorie"], ascending=[True, True]).reset_index(
        drop=True
    )


def get_statement_summary(df_long: pd.DataFrame, thresholds: ThresholdConfig) -> pd.DataFrame:
    summary = _group_summary(
        df_long,
        ["kompetenzfeld", "unterkategorie", "aussage"],
        thresholds,
    )
    return summary.sort_values(["avg_score", "aussage"], ascending=[True, True]).reset_index(
        drop=True
    )


def get_employee_summary(df_long: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df_long.groupby("mitarbeiter", dropna=False)
        .agg(
            avg_score=("score", "mean"),
            weak_responses=("is_weak", "sum"),
            expert_responses=("is_expert", "sum"),
            field_count=("kompetenzfeld", "nunique"),
            subcategory_count=("unterkategorie", "nunique"),
        )
        .reset_index()
        .sort_values(["avg_score", "mitarbeiter"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return summary


def get_bottlenecks(df_long: pd.DataFrame, thresholds: ThresholdConfig) -> pd.DataFrame:
    summary = get_subcategory_summary(df_long, thresholds)
    bottlenecks = summary[summary["bottleneck"] | summary["no_expert"]].copy()
    return bottlenecks.sort_values(
        ["no_expert", "bottleneck", "avg_score"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def get_heatmap_data(df_long: pd.DataFrame) -> pd.DataFrame:
    return df_long.pivot_table(
        index="unterkategorie",
        columns="mitarbeiter",
        values="score",
        aggfunc="mean",
    ).sort_index()


def get_employee_profile_scores(df_long: pd.DataFrame, employee: str) -> pd.DataFrame:
    employee_df = df_long[df_long["mitarbeiter"] == employee]
    summary = (
        employee_df.groupby("kompetenzfeld", dropna=False)
        .agg(avg_score=("score", "mean"))
        .reset_index()
        .sort_values(["avg_score", "kompetenzfeld"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return summary


def get_employee_focus_areas(
    df_long: pd.DataFrame,
    employee: str,
    *,
    limit: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    employee_df = df_long[df_long["mitarbeiter"] == employee][
        ["unterkategorie", "aussage", "score"]
    ].copy()
    strengths = employee_df.sort_values(["score", "aussage"], ascending=[False, True]).head(limit)
    development = employee_df.sort_values(["score", "aussage"], ascending=[True, True]).head(limit)
    return strengths.reset_index(drop=True), development.reset_index(drop=True)
