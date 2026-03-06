from __future__ import annotations

import pandas as pd
import pytest

from src.config import DEFAULT_THRESHOLDS
from src.metrics import (
    get_bottlenecks,
    get_employee_focus_areas,
    get_overview_metrics,
    get_subcategory_summary,
)


def build_dataset() -> pd.DataFrame:
    rows = [
        ("Netzwerk", "Routing", "S1", "Alice", 4.0),
        ("Netzwerk", "Routing", "S1", "Bob", 2.0),
        ("Netzwerk", "Routing", "S2", "Alice", 4.0),
        ("Netzwerk", "Routing", "S2", "Bob", 1.0),
        ("Security", "IAM", "S3", "Alice", 1.0),
        ("Security", "IAM", "S3", "Bob", 2.0),
        ("Security", "IAM", "S4", "Alice", 1.0),
        ("Security", "IAM", "S4", "Bob", 4.0),
    ]
    frame = pd.DataFrame(
        rows,
        columns=["kompetenzfeld", "unterkategorie", "aussage", "mitarbeiter", "score"],
    )
    frame["score_valid"] = True
    frame["is_expert"] = frame["score"] >= DEFAULT_THRESHOLDS.expert_threshold
    frame["is_weak"] = frame["score"] <= DEFAULT_THRESHOLDS.weak_threshold
    return frame


def test_subcategory_summary_computes_bus_factor_and_flags() -> None:
    summary = get_subcategory_summary(build_dataset(), DEFAULT_THRESHOLDS)

    routing = summary.loc[summary["unterkategorie"] == "Routing"].iloc[0]
    iam = summary.loc[summary["unterkategorie"] == "IAM"].iloc[0]

    assert routing["bus_factor"] == 1
    assert routing["bottleneck"]
    assert not routing["no_expert"]
    assert routing["avg_score"] == pytest.approx(2.75)

    assert iam["bus_factor"] == 0
    assert not iam["bottleneck"]
    assert iam["no_expert"]
    assert iam["avg_score"] == pytest.approx(2.0)


def test_overview_metrics_and_bottleneck_selection() -> None:
    dataset = build_dataset()
    overview = get_overview_metrics(dataset, DEFAULT_THRESHOLDS)
    bottlenecks = get_bottlenecks(dataset, DEFAULT_THRESHOLDS)

    assert overview["field_count"] == 2
    assert overview["subcategory_count"] == 2
    assert overview["employee_count"] == 2
    assert overview["bottleneck_count"] == 1
    assert overview["no_expert_count"] == 1
    assert overview["skill_coverage_index"] == pytest.approx(0.0)
    assert set(bottlenecks["unterkategorie"]) == {"Routing", "IAM"}


def test_employee_focus_areas_are_sorted() -> None:
    strengths, development = get_employee_focus_areas(build_dataset(), "Alice", limit=2)

    assert list(strengths["score"]) == [4.0, 4.0]
    assert list(development["score"]) == [1.0, 1.0]
