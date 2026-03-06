from __future__ import annotations

from dataclasses import dataclass

APP_TITLE = "Kompetenzanalyse IT"
DEFAULT_DATA_FILE = "kompetenzdaten.json"
DATA_NOTE = (
    "Die Auswertung basiert auf Selbsteinschätzungen und dient als Orientierung für "
    "Risikoreduktion, Weiterentwicklung und Teamresilienz."
)


@dataclass(frozen=True, slots=True)
class ThresholdConfig:
    expert_threshold: int = 4
    weak_threshold: int = 2
    min_score: int = 1
    max_score: int = 5
    target_redundancy: int = 2


DEFAULT_THRESHOLDS = ThresholdConfig()
