from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import DEFAULT_THRESHOLDS
from src.data_loader import detect_header_row, load_assessment_data


def write_workbook(path: Path, *, sheet_name: str) -> None:
    rows = [
        [None, None, None, None, None],
        ["Meta", None, None, None, None],
        ["Kompetenzfeld", "Unterkategorie", "Aussage", "Alice", "Bob"],
        ["Netzwerk", "Routing", "Switching", 4, 2],
        ["Netzwerk", "Routing", "Firewalls", "n/a", 5],
        ["Security", "IAM", "MFA", None, 6],
    ]
    frame = pd.DataFrame(rows)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name=sheet_name, header=False, index=False)


def test_detect_header_row_finds_expected_index() -> None:
    raw_df = pd.DataFrame(
        [
            [None, None, None],
            ["foo", "bar", "baz"],
            ["Kompetenzfeld", "Unterkategorie", "Aussage"],
        ]
    )
    assert detect_header_row(raw_df) == 2


def test_load_assessment_data_transforms_and_warns(tmp_path: Path) -> None:
    workbook = tmp_path / "kompetenzen.xlsx"
    write_workbook(workbook, sheet_name="Selbsteinschätzung")

    result = load_assessment_data(workbook, thresholds=DEFAULT_THRESHOLDS)

    assert list(result.data.columns) == [
        "kompetenzfeld",
        "unterkategorie",
        "aussage",
        "mitarbeiter",
        "score",
        "score_valid",
        "is_expert",
        "is_weak",
    ]
    assert result.metadata.row_count == 3
    assert result.metadata.employee_count == 2
    assert result.metadata.subcategory_count == 1
    issue_messages = {issue.message for issue in result.issues}
    assert "1 nicht numerische Scores wurden ignoriert." in issue_messages
    assert "1 Scores außerhalb der Skala 1-5 wurden ignoriert." in issue_messages


def test_load_assessment_data_falls_back_to_first_sheet(tmp_path: Path) -> None:
    workbook = tmp_path / "kompetenzen.xlsx"
    write_workbook(workbook, sheet_name="Input")

    result = load_assessment_data(workbook, thresholds=DEFAULT_THRESHOLDS)

    assert result.metadata.sheet_name == "Input"
    assert any("Stattdessen wird 'Input' ausgewertet." in issue.message for issue in result.issues)
