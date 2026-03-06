from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    create_employee_bar_chart,
    create_heatmap,
    create_ranked_bar_chart,
    create_risk_scatter,
)
from src.config import APP_TITLE, DATA_NOTE, DEFAULT_DATA_FILE, DEFAULT_THRESHOLDS
from src.data_loader import DataLoadError, LoadResult, load_assessment_data
from src.metrics import (
    get_bottlenecks,
    get_employee_focus_areas,
    get_employee_profile_scores,
    get_employee_summary,
    get_field_summary,
    get_heatmap_data,
    get_overview_metrics,
    get_statement_summary,
    get_subcategory_summary,
)

st.set_page_config(page_title=APP_TITLE, layout="wide")

TABLE_LABELS = {
    "kompetenzfeld": "Kompetenzfeld",
    "unterkategorie": "Unterkategorie",
    "aussage": "Aussage",
    "mitarbeiter": "Mitarbeitende",
    "score": "Bewertung",
    "avg_score": "Durchschnitt",
    "median_score": "Median",
    "score_std": "Standardabweichung",
    "weak_share": "Schwachanteil",
    "response_count": "Anzahl Bewertungen",
    "statement_count": "Anzahl Aussagen",
    "employee_count": "Anzahl Mitarbeitende",
    "bus_factor": "Bus-Faktor",
    "expert_count": "Anzahl Expert:innen",
    "bottleneck": "Flaschenhals",
    "no_expert": "Ohne Expert:innen",
    "coverage_ratio": "Abdeckungsquote",
    "weak_responses": "Anzahl schwache Bewertungen",
    "expert_responses": "Anzahl starke Bewertungen",
}


@st.cache_data(show_spinner=False)
def load_dataset(path_str: str) -> LoadResult:
    return load_assessment_data(Path(path_str), thresholds=DEFAULT_THRESHOLDS)


@st.cache_data(show_spinner=False, max_entries=32)
def get_cached_views(
    df_long: pd.DataFrame,
) -> tuple[
    dict[str, int | float],
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    return (
        get_overview_metrics(df_long, DEFAULT_THRESHOLDS),
        get_field_summary(df_long, DEFAULT_THRESHOLDS),
        get_subcategory_summary(df_long, DEFAULT_THRESHOLDS),
        get_statement_summary(df_long, DEFAULT_THRESHOLDS),
        get_employee_summary(df_long),
        get_bottlenecks(df_long, DEFAULT_THRESHOLDS),
        get_heatmap_data(df_long),
    )


def apply_filters(df_long: pd.DataFrame, subcategory_summary: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.header("Filter")
        all_fields = sorted(df_long["kompetenzfeld"].unique().tolist())
        selected_fields = st.multiselect(
            "Kompetenzfelder",
            options=all_fields,
            default=all_fields,
        )

        field_filtered = df_long[df_long["kompetenzfeld"].isin(selected_fields)]
        available_subcategories = sorted(field_filtered["unterkategorie"].unique().tolist())
        selected_subcategories = st.multiselect(
            "Unterkategorien",
            options=available_subcategories,
            default=available_subcategories,
        )

        subcategory_filtered = field_filtered[
            field_filtered["unterkategorie"].isin(selected_subcategories)
        ]
        all_employees = sorted(subcategory_filtered["mitarbeiter"].unique().tolist())
        selected_employees = st.multiselect(
            "Mitarbeitende",
            options=all_employees,
            default=all_employees,
        )

        show_critical_only = st.toggle("Nur kritische Themen", value=False)
        show_bottlenecks_only = st.toggle("Nur Flaschenhälse", value=False)
        show_no_experts_only = st.toggle("Nur Themen ohne Expert:innen", value=False)

        st.caption(DATA_NOTE)

    filtered = subcategory_filtered[subcategory_filtered["mitarbeiter"].isin(selected_employees)]
    if filtered.empty:
        return filtered

    if show_critical_only or show_bottlenecks_only or show_no_experts_only:
        scoped_summary = subcategory_summary[
            subcategory_summary["unterkategorie"].isin(filtered["unterkategorie"].unique())
        ].copy()
        scoped_summary["is_critical"] = (
            (scoped_summary["avg_score"] <= DEFAULT_THRESHOLDS.weak_threshold + 1)
            | scoped_summary["bottleneck"]
            | scoped_summary["no_expert"]
        )

        if show_critical_only:
            scoped_summary = scoped_summary[scoped_summary["is_critical"]]
        if show_bottlenecks_only:
            scoped_summary = scoped_summary[scoped_summary["bottleneck"]]
        if show_no_experts_only:
            scoped_summary = scoped_summary[scoped_summary["no_expert"]]

        filtered = filtered[filtered["unterkategorie"].isin(scoped_summary["unterkategorie"])]

    return filtered


def render_interpretation(text: str) -> None:
    st.caption(f"Interpretation: {text}")


def localize_table(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    display_df = df.copy()
    if columns is not None:
        display_df = display_df[columns].copy()

    boolean_columns = display_df.select_dtypes(include="bool").columns
    for column_name in boolean_columns:
        display_df[column_name] = display_df[column_name].map({True: "Ja", False: "Nein"})

    return display_df.rename(columns=TABLE_LABELS)


def render_overview(
    overview: dict[str, int | float],
    field_summary: pd.DataFrame,
    subcategory_summary: pd.DataFrame,
) -> None:
    st.subheader("Management-Überblick")
    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Kompetenzfelder",
        int(overview["field_count"]),
        help="Anzahl der übergeordneten Themenbereiche in der Auswertung.",
    )
    metric_columns[1].metric(
        "Unterkategorien",
        int(overview["subcategory_count"]),
        help=(
            "Anzahl der fachlich konkreteren Themen, die für Risiko und Abdeckung "
            "betrachtet werden."
        ),
    )
    metric_columns[2].metric(
        "Aussagen",
        int(overview["statement_count"]),
        help="Anzahl der einzelnen Bewertungsfragen aus der Excel-Datei.",
    )
    metric_columns[3].metric(
        "Mitarbeitende",
        int(overview["employee_count"]),
        help="Anzahl der Personen, für die gültige Selbstbewertungen vorliegen.",
    )

    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Gesamtdurchschnitt",
        f"{overview['overall_avg']:.2f}",
        help="Mittelwert über alle gültigen Selbstbewertungen im aktuellen Filterkontext.",
    )
    metric_columns[1].metric(
        "Skill-Coverage-Index",
        f"{overview['skill_coverage_index']:.0%}",
        help="Anteil der Unterkategorien mit mindestens zwei ausreichend starken Personen.",
    )
    metric_columns[2].metric(
        "Flaschenhälse",
        int(overview["bottleneck_count"]),
        help="Unterkategorien mit genau einer Person auf hohem Kompetenzniveau.",
    )
    metric_columns[3].metric(
        "Themen ohne Expert:innen",
        int(overview["no_expert_count"]),
        help=(
            "Unterkategorien, in denen aktuell niemand das definierte "
            "Expert:innen-Niveau erreicht."
        ),
    )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            create_ranked_bar_chart(
                field_summary,
                category_col="kompetenzfeld",
                value_col="avg_score",
                title="Stärkste Kompetenzfelder",
                ascending=False,
            ),
            use_container_width=True,
        )
        render_interpretation(
            "Weiter rechts und höher platzierte Balken zeigen Kompetenzfelder, in denen das "
            "Team im Mittel besonders stark aufgestellt ist."
        )
    with right:
        st.plotly_chart(
            create_ranked_bar_chart(
                subcategory_summary,
                category_col="unterkategorie",
                value_col="avg_score",
                title="Kritischste Unterkategorien",
                ascending=True,
            ),
            use_container_width=True,
        )
        render_interpretation(
            "Niedrige Balken markieren Unterkategorien mit erhöhtem Handlungsbedarf, weil der "
            "durchschnittliche Selbstwert dort am schwächsten ausfällt."
        )


def render_strengths_and_gaps(
    field_summary: pd.DataFrame,
    subcategory_summary: pd.DataFrame,
) -> None:
    st.subheader("Stärken und Lücken")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            create_ranked_bar_chart(
                field_summary,
                category_col="kompetenzfeld",
                value_col="avg_score",
                title="Top-Kompetenzfelder",
                ascending=False,
            ),
            use_container_width=True,
        )
        render_interpretation(
            "Diese Grafik priorisiert die stärksten Kompetenzfelder. Hohe Werte deuten auf "
            "breit vorhandenes oder stabiles Know-how hin."
        )
        st.dataframe(
            localize_table(
                field_summary,
                ["kompetenzfeld", "avg_score", "bus_factor", "weak_share"],
            ),
            hide_index=True,
            use_container_width=True,
        )
        render_interpretation(
            "Die Tabelle kombiniert Stärke und Risiko: hoher Durchschnitt und hoher "
            "Bus-Faktor sind robust, hoher Schwachanteil relativiert gute Mittelwerte."
        )
    with right:
        st.plotly_chart(
            create_ranked_bar_chart(
                subcategory_summary,
                category_col="unterkategorie",
                value_col="avg_score",
                title="Schwächste Unterkategorien",
                ascending=True,
            ),
            use_container_width=True,
        )
        render_interpretation(
            "Diese Grafik zeigt die schwächsten Unterkategorien zuerst. Sie eignet sich als "
            "erste Liste für Trainings- oder Unterstützungsbedarf."
        )
        st.dataframe(
            localize_table(
                subcategory_summary,
                [
                    "unterkategorie",
                    "avg_score",
                    "expert_count",
                    "weak_share",
                    "no_expert",
                ],
            ),
            hide_index=True,
            use_container_width=True,
        )
        render_interpretation(
            "Achte auf Unterkategorien mit niedrigem Durchschnitt, hohem Schwachanteil und dem "
            "Flag 'Ohne Expert:innen' - dort fehlt aktuell belastbare Abdeckung."
        )


def render_risks(subcategory_summary: pd.DataFrame, bottlenecks: pd.DataFrame) -> None:
    st.subheader("Risiko und Abdeckung")
    st.info(
        "Bus-Faktor: Anzahl Personen, die eine Unterkategorie im Mittel auf hohem Niveau "
        "abdecken. Ein Flaschenhals liegt bei genau einer solchen Person vor."
    )

    left, right = st.columns([3, 2])
    with left:
        st.dataframe(
            localize_table(
                bottlenecks,
                [
                    "unterkategorie",
                    "avg_score",
                    "bus_factor",
                    "expert_count",
                    "weak_share",
                    "bottleneck",
                    "no_expert",
                ],
            ),
            hide_index=True,
            use_container_width=True,
        )
        render_interpretation(
            "Diese Tabelle listet kritische Unterkategorien. Ein Flaschenhals bedeutet genau "
            "eine starke Person, 'Ohne Expert:innen' signalisiert fehlende Abdeckung."
        )
    with right:
        st.plotly_chart(
            create_risk_scatter(subcategory_summary, "Durchschnitt vs. Bus-Faktor"),
            use_container_width=True,
        )
        render_interpretation(
            "Punkte links unten sind am kritischsten: niedriger Durchschnitt und zugleich "
            "wenige starke Personen. Rechts oben liegt robuste Teamabdeckung."
        )


def render_employee_profile(df_long: pd.DataFrame) -> None:
    st.subheader("Mitarbeitendenprofil")
    employees = sorted(df_long["mitarbeiter"].unique().tolist())
    selected_employee = st.selectbox("Person", employees)

    profile_scores = get_employee_profile_scores(df_long, selected_employee)
    strengths, development = get_employee_focus_areas(df_long, selected_employee)

    left, right = st.columns([2, 1])
    with left:
        st.plotly_chart(
            create_employee_bar_chart(
                profile_scores,
                employee=selected_employee,
                title=f"Durchschnitt je Kompetenzfeld: {selected_employee}",
            ),
            use_container_width=True,
        )
        render_interpretation(
            "Die Balken zeigen, in welchen Kompetenzfeldern diese Person sich selbst stärker "
            "oder schwächer einschätzt. Größere Unterschiede deuten auf ein "
            "spezialisiertes Profil hin."
        )
    with right:
        st.dataframe(
            localize_table(
                strengths.rename(columns={"aussage": "Stärke"}),
            ),
            hide_index=True,
            use_container_width=True,
        )
        render_interpretation(
            "Hier stehen die am höchsten bewerteten Aussagen dieser Person. Das sind naheliegende "
            "Themen für Wissenstransfer oder Mentoring."
        )
        st.dataframe(
            localize_table(
                development.rename(columns={"aussage": "Entwicklungsfeld"}),
            ),
            hide_index=True,
            use_container_width=True,
        )
        render_interpretation(
            "Diese Aussagen wurden am niedrigsten bewertet. Sie zeigen individuelle "
            "Entwicklungsfelder oder Themen mit Unterstützungsbedarf."
        )


def render_heatmap(heatmap_data: pd.DataFrame) -> None:
    st.subheader("Heatmap Unterkategorie x Mitarbeitende")
    st.plotly_chart(
        create_heatmap(heatmap_data, "Durchschnittsscores je Unterkategorie"),
        use_container_width=True,
    )
    render_interpretation(
        "Grün steht für hohe, Rot für niedrige Selbstbewertungen. Auffällige Farbunterschiede "
        "innerhalb einer Zeile deuten auf ungleich verteiltes Wissen hin."
    )


def render_app(load_result: LoadResult) -> None:
    st.title(APP_TITLE)
    st.caption(DATA_NOTE)

    if load_result.issues:
        with st.expander("Validierungshinweise", expanded=True):
            for issue in load_result.issues:
                if issue.severity == "warning":
                    st.warning(issue.message)
                else:
                    st.error(issue.message)

    _, _, subcategory_summary, _, _, _, _ = get_cached_views(load_result.data)

    filtered_data = apply_filters(load_result.data, subcategory_summary)
    if filtered_data.empty:
        st.warning("Die aktuelle Filterkombination liefert keine gültigen Bewertungen.")
        return

    (
        filtered_overview,
        filtered_field_summary,
        filtered_subcategory_summary,
        filtered_statement_summary,
        filtered_employee_summary,
        filtered_bottlenecks,
        filtered_heatmap_data,
    ) = get_cached_views(filtered_data)

    st.caption(
        f"Quelle: {load_result.metadata.sheet_name} | "
        f"Gültige Bewertungen: {load_result.metadata.row_count}"
    )

    view = st.segmented_control(
        "Bereich",
        options=[
            "Überblick",
            "Stärken & Lücken",
            "Risiko",
            "Mitarbeitendenprofil",
            "Heatmap",
            "Details",
        ],
        default="Überblick",
    )

    if view == "Überblick":
        render_overview(filtered_overview, filtered_field_summary, filtered_subcategory_summary)
    elif view == "Stärken & Lücken":
        render_strengths_and_gaps(filtered_field_summary, filtered_subcategory_summary)
    elif view == "Risiko":
        render_risks(filtered_subcategory_summary, filtered_bottlenecks)
    elif view == "Mitarbeitendenprofil":
        render_employee_profile(filtered_data)
    elif view == "Heatmap":
        render_heatmap(filtered_heatmap_data)
    else:
        st.subheader("Detailtabellen")
        left, right = st.columns(2)
        with left:
            st.dataframe(
                localize_table(filtered_subcategory_summary),
                hide_index=True,
                use_container_width=True,
            )
            render_interpretation(
                "Diese Detailtabelle zeigt die vollständige Bewertung je Unterkategorie und ist "
                "die beste Grundlage für priorisierte Maßnahmen auf Themenebene."
            )
        with right:
            st.dataframe(
                localize_table(filtered_statement_summary),
                hide_index=True,
                use_container_width=True,
            )
            render_interpretation(
                "Die Aussagen-Tabelle macht sichtbar, welche konkreten Einzelthemen einen "
                "niedrigen Durchschnitt nach unten ziehen."
            )
        st.dataframe(
            localize_table(filtered_employee_summary),
            hide_index=True,
            use_container_width=True,
        )
        render_interpretation(
            "Die Mitarbeitendenübersicht vergleicht das Gesamtprofil der Personen. Hohe "
            "Expert:innen-Anteile bei gleichzeitig vielen Schwachstellen können auf "
            "Spezialisierung hindeuten."
        )


def main() -> None:
    data_path = Path(__file__).with_name(DEFAULT_DATA_FILE)
    if not data_path.exists():
        st.error(
            "Die Excel-Datei wurde nicht gefunden. "
            f"Bitte lege '{DEFAULT_DATA_FILE}' im Projektroot ab."
        )
        st.stop()

    try:
        load_result = load_dataset(str(data_path))
    except DataLoadError as exc:
        st.error(str(exc))
        st.stop()

    render_app(load_result)


main()
