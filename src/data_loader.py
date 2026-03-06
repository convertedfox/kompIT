from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd

from src.config import PREFERRED_SHEET_NAME, REQUIRED_HEADERS, ThresholdConfig


class DataLoadError(ValueError):
    """Raised when the Excel file cannot be parsed into the expected shape."""


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    message: str
    severity: Literal["warning", "error"] = "warning"


@dataclass(frozen=True, slots=True)
class DatasetMetadata:
    source_path: str
    sheet_name: str
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


def detect_header_row(raw_df: pd.DataFrame) -> int:
    required = {header.casefold() for header in REQUIRED_HEADERS}
    for row_index in range(len(raw_df.index)):
        row_values = {normalize_header(value) for value in raw_df.iloc[row_index].tolist()}
        if required.issubset(row_values):
            return row_index
    raise DataLoadError(
        "Keine passende Kopfzeile gefunden. Erwartet werden die Spalten "
        "'Kompetenzfeld', 'Unterkategorie' und 'Aussage'."
    )


def select_sheet_name(
    excel_file: pd.ExcelFile,
    preferred_sheet: str = PREFERRED_SHEET_NAME,
) -> tuple[str, tuple[ValidationIssue, ...]]:
    if preferred_sheet in excel_file.sheet_names:
        return preferred_sheet, ()
    if not excel_file.sheet_names:
        raise DataLoadError("Die Excel-Datei enthält keine Arbeitsblätter.")
    selected_sheet = excel_file.sheet_names[0]
    return selected_sheet, (
        ValidationIssue(
            "Das Blatt 'Selbsteinschätzung' wurde nicht gefunden. "
            f"Stattdessen wird '{selected_sheet}' ausgewertet."
        ),
    )


def _prepare_base_frame(raw_df: pd.DataFrame, header_row: int) -> tuple[pd.DataFrame, list[str]]:
    header_values = [normalize_text(value) for value in raw_df.iloc[header_row].tolist()]
    normalized_headers = [header.casefold() for header in header_values]
    header_lookup = {header: index for index, header in enumerate(normalized_headers) if header}

    required_indices = [header_lookup[header.casefold()] for header in REQUIRED_HEADERS]
    statement_index = required_indices[-1]

    employee_columns = [
        column_index
        for column_index in range(statement_index + 1, len(header_values))
        if header_values[column_index]
    ]
    if not employee_columns:
        raise DataLoadError(
            "Es wurden keine Mitarbeitenden-Spalten nach der Spalte 'Aussage' gefunden."
        )

    employee_names = [header_values[column_index] for column_index in employee_columns]
    if len(set(employee_names)) != len(employee_names):
        raise DataLoadError("Mitarbeitenden-Spalten müssen eindeutige Namen haben.")

    selected_columns = [*required_indices, *employee_columns]
    prepared = raw_df.iloc[header_row + 1 :, selected_columns].copy()
    prepared.columns = ["kompetenzfeld", "unterkategorie", "aussage", *employee_names]
    prepared = prepared.dropna(how="all")

    for column_name in ("kompetenzfeld", "unterkategorie"):
        cleaned = prepared[column_name].map(normalize_text)
        prepared[column_name] = cleaned.replace("", pd.NA).ffill().fillna("")
    prepared["aussage"] = prepared["aussage"].map(normalize_text)
    prepared = prepared[prepared["aussage"] != ""].copy()
    return prepared, employee_names


def _build_long_format(
    prepared_df: pd.DataFrame,
    employee_names: list[str],
    thresholds: ThresholdConfig,
) -> tuple[pd.DataFrame, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    long_df = prepared_df.melt(
        id_vars=["kompetenzfeld", "unterkategorie", "aussage"],
        value_vars=employee_names,
        var_name="mitarbeiter",
        value_name="score_input",
    )
    long_df["mitarbeiter"] = long_df["mitarbeiter"].map(normalize_text)
    long_df["score_input"] = long_df["score_input"].map(normalize_text)

    non_empty_scores = long_df[long_df["score_input"] != ""].copy()
    if non_empty_scores.empty:
        raise DataLoadError("Es wurden keine auswertbaren Scores in der Excel-Datei gefunden.")

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
            ValidationIssue(
                f"{invalid_text_count} nicht numerische Scores wurden ignoriert.",
            )
        )
    if out_of_range_count:
        issues.append(
            ValidationIssue(
                f"{out_of_range_count} Scores außerhalb der Skala "
                f"{thresholds.min_score}-{thresholds.max_score} wurden ignoriert.",
            )
        )

    return cleaned.reset_index(drop=True), issues


def load_assessment_data(
    path: str | Path,
    *,
    preferred_sheet: str = PREFERRED_SHEET_NAME,
    thresholds: ThresholdConfig,
) -> LoadResult:
    source_path = Path(path)
    if not source_path.exists():
        raise DataLoadError(f"Die Datei '{source_path.name}' wurde nicht gefunden.")

    excel_file = pd.ExcelFile(source_path, engine="openpyxl")
    sheet_name, selection_issues = select_sheet_name(excel_file, preferred_sheet)
    raw_df = pd.read_excel(
        source_path,
        sheet_name=sheet_name,
        header=None,
        engine="openpyxl",
        dtype=object,
        keep_default_na=False,
    )
    header_row = detect_header_row(raw_df)
    prepared_df, employee_names = _prepare_base_frame(raw_df, header_row)
    df_long, build_issues = _build_long_format(prepared_df, employee_names, thresholds)

    metadata = DatasetMetadata(
        source_path=str(source_path),
        sheet_name=sheet_name,
        row_count=int(len(df_long.index)),
        employee_count=int(df_long["mitarbeiter"].nunique()),
        field_count=int(df_long["kompetenzfeld"].nunique()),
        subcategory_count=int(df_long["unterkategorie"].nunique()),
        statement_count=int(df_long["aussage"].nunique()),
    )
    return LoadResult(
        data=df_long,
        metadata=metadata,
        issues=(*selection_issues, *build_issues),
    )
