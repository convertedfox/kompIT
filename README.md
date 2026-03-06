# Kompetenzanalyse IT

Streamlit-Dashboard zur Auswertung von Excel-Selbsteinschätzungen für IT-Teams. Die App macht Stärken, Lücken und Wissensmonopole sichtbar, ohne einzelne Personen als Leistungsurteil zu framen.

## Installation

```bash
uv sync --dev
```

## Start

```bash
uv run streamlit run app.py
```

Die App erwartet die Datei `IT Kompetenz Zusammenfassung - anonymisiert.xlsx` im Projektroot.

## Erwartete Excel-Struktur

- Bevorzugtes Blatt: `Selbsteinschätzung`
- Kopfzeile mit:
  - `Kompetenzfeld`
  - `Unterkategorie`
  - `Aussage`
  - danach dynamisch beliebig viele Mitarbeitenden-Spalten
- Werte in den Mitarbeitenden-Spalten: numerische Selbsteinschätzungen von `1` bis `5`

Leere Scores werden ignoriert. Nicht numerische oder außerhalb der Skala liegende Werte werden als Warnung gemeldet und nicht ausgewertet.

## Wichtige Kennzahlen

- `Gesamtdurchschnitt`: Mittelwert über alle gültigen Bewertungen
- `Skill-Coverage-Index`: Anteil der Unterkategorien mit mindestens zwei Personen auf hohem Niveau
- `Bus-Faktor`: Anzahl Personen, die eine Unterkategorie im Mittel auf Expert:innen-Niveau (`>= 4`) abdecken
- `Flaschenhals`: Unterkategorie mit genau einer entsprechend starken Person
- `Thema ohne Expert:innen`: Unterkategorie ohne Person auf hohem Niveau

## Qualitätssicherung

```bash
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pytest
```
