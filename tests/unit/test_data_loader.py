from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import DEFAULT_THRESHOLDS
from src.data_loader import DataLoadError, load_assessment_data


def write_records(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def test_load_assessment_data_transforms_and_warns(tmp_path: Path) -> None:
    source = tmp_path / "kompetenzen.json"
    write_records(
        source,
        [
            {
                "kompetenzfeld": "Netzwerk",
                "unterkategorie": "Routing",
                "aussage": "Switching",
                "mitarbeiter": "Alice",
                "score": 4,
            },
            {
                "kompetenzfeld": "Netzwerk",
                "unterkategorie": "Routing",
                "aussage": "Switching",
                "mitarbeiter": "Bob",
                "score": 2,
            },
            {
                "kompetenzfeld": "Netzwerk",
                "unterkategorie": "Routing",
                "aussage": "Firewalls",
                "mitarbeiter": "Alice",
                "score": "n/a",
            },
            {
                "kompetenzfeld": "Netzwerk",
                "unterkategorie": "Routing",
                "aussage": "Firewalls",
                "mitarbeiter": "Bob",
                "score": 5,
            },
            {
                "kompetenzfeld": "Security",
                "unterkategorie": "IAM",
                "aussage": "MFA",
                "mitarbeiter": "Bob",
                "score": 6,
            },
        ],
    )

    result = load_assessment_data(source, thresholds=DEFAULT_THRESHOLDS)

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
    assert result.metadata.source_name == "kompetenzen.json"
    issue_messages = {issue.message for issue in result.issues}
    assert "1 nicht numerische Scores wurden ignoriert." in issue_messages
    assert "1 Scores außerhalb der Skala 1-5 wurden ignoriert." in issue_messages


def test_load_assessment_data_rejects_missing_required_columns(tmp_path: Path) -> None:
    source = tmp_path / "kompetenzen.json"
    write_records(
        source,
        [
            {
                "kompetenzfeld": "Netzwerk",
                "unterkategorie": "Routing",
                "aussage": "Switching",
                "score": 4,
            }
        ],
    )

    with pytest.raises(DataLoadError, match="Pflichtfelder"):
        load_assessment_data(source, thresholds=DEFAULT_THRESHOLDS)
