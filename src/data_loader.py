from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd

from src.config import ThresholdConfig

REQUIRED_COLUMNS = ("kompetenzfeld", "unterkategorie", "aussage", "mitarbeiter", "score")


class DataLoadError(ValueError):
    """Raised when the source file cannot be parsed into the expected shape."""


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    message: str
    severity: Literal["warning", "error"] = "warning"


@dataclass(frozen=True, slots=True)
class DatasetMetadata:
    source_path: str
    source_name: str
    row_count: int
    employee_count: int
    field_count: int
    subcategory_count: int
    statement_count: int


@dataclass(frozen=True, slots=True)
class LoadResult:
    data: pd.DataFrame
    metadata: DatasetMetadata
    issues: tuple[ValidationIssue, ...]


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_header(value: object) -> str:
    return normalize_text(value).casefold()


def _load_raw_json(source_path: Path) -> pd.DataFrame:
    try:
        raw_content = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataLoadError(f"Die JSON-Datei ist ungültig: {exc.msg}.") from exc

    if not isinstance(raw_content, list):
        raise DataLoadError(
            "Die JSON-Datei muss eine Liste von Datensätzen im Long-Format enthalten."
        )

    raw_df = pd.DataFrame(raw_content)
    if raw_df.empty:
        raise DataLoadError("Die JSON-Datei enthält keine Datensätze.")

    normalized_columns = {column: normalize_header(column) for column in raw_df.columns}
    raw_df = raw_df.rename(columns=normalized_columns)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in raw_df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise DataLoadError(f"Der JSON-Datei fehlen Pflichtfelder: {missing_text}.")

    prepared = raw_df.loc[:, list(REQUIRED_COLUMNS)].copy()
    for column_name in ("kompetenzfeld", "unterkategorie", "aussage", "mitarbeiter"):
        prepared[column_name] = prepared[column_name].map(normalize_text)

    prepared = prepared[
        (prepared["kompetenzfeld"] != "")
        & (prepared["unterkategorie"] != "")
        & (prepared["aussage"] != "")
        & (prepared["mitarbeiter"] != "")
    ].copy()
    if prepared.empty:
        raise DataLoadError("Die JSON-Datei enthält keine vollständig befüllten Datensätze.")

    return prepared


def _build_long_format(
    prepared_df: pd.DataFrame,
    thresholds: ThresholdConfig,
) -> tuple[pd.DataFrame, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    prepared_df = prepared_df.copy()
    prepared_df["score_input"] = prepared_df["score"].map(normalize_text)

    non_empty_scores = prepared_df[prepared_df["score_input"] != ""].copy()
    if non_empty_scores.empty:
        raise DataLoadError("Es wurden keine auswertbaren Scores in der JSON-Datei gefunden.")

    numeric_scores = pd.to_numeric(
        non_empty_scores["score_input"].str.replace(",", ".", regex=False),
        errors="coerce",
    )
    non_empty_scores["score"] = numeric_scores

    invalid_text_count = int(non_empty_scores["score"].isna().sum())
    out_of_range_mask = non_empty_scores["score"].notna() & ~non_empty_scores["score"].between(
        thresholds.min_score,
        thresholds.max_score,
    )
    out_of_range_count = int(out_of_range_mask.sum())

    cleaned = non_empty_scores[non_empty_scores["score"].notna() & ~out_of_range_mask].copy()
    if cleaned.empty:
        raise DataLoadError("Alle vorhandenen Scores waren ungültig oder außerhalb der Skala.")

    cleaned["score"] = cleaned["score"].astype(float)
    cleaned["score_valid"] = True
    cleaned["is_expert"] = cleaned["score"] >= thresholds.expert_threshold
    cleaned["is_weak"] = cleaned["score"] <= thresholds.weak_threshold
    cleaned = cleaned[
        [
            "kompetenzfeld",
            "unterkategorie",
            "aussage",
            "mitarbeiter",
            "score",
            "score_valid",
            "is_expert",
            "is_weak",
        ]
    ].sort_values(["kompetenzfeld", "unterkategorie", "aussage", "mitarbeiter"])

    if invalid_text_count:
        issues.append(
            ValidationIssue(f"{invalid_text_count} nicht numerische Scores wurden ignoriert.")
        )
    if out_of_range_count:
        issues.append(
            ValidationIssue(
                f"{out_of_range_count} Scores außerhalb der Skala "
                f"{thresholds.min_score}-{thresholds.max_score} wurden ignoriert."
            )
        )

    return cleaned.reset_index(drop=True), issues


def load_assessment_data(
    path: str | Path,
    *,
    thresholds: ThresholdConfig,
) -> LoadResult:
    source_path = Path(path)
    if not source_path.exists():
        raise DataLoadError(f"Die Datei '{source_path.name}' wurde nicht gefunden.")

    prepared_df = _load_raw_json(source_path)
    df_long, build_issues = _build_long_format(prepared_df, thresholds)

    metadata = DatasetMetadata(
        source_path=str(source_path),
        source_name=source_path.name,
        row_count=int(len(df_long.index)),
        employee_count=int(df_long["mitarbeiter"].nunique()),
        field_count=int(df_long["kompetenzfeld"].nunique()),
        subcategory_count=int(df_long["unterkategorie"].nunique()),
        statement_count=int(df_long["aussage"].nunique()),
    )
    return LoadResult(
        data=df_long,
        metadata=metadata,
        issues=tuple(build_issues),
    )
