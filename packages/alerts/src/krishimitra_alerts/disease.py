from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DiseaseAlert:
    disease: str
    severity: str
    action: str

class DiseaseAlertGenerator:
    def generate(self, disease: str, severity: str) -> DiseaseAlert:
        actions = {
            "high": "Apply fungicide immediately and isolate affected plants.",
            "moderate": "Monitor closely and prepare preventive spray.",
            "low": "Continue routine scouting.",
        }
        return DiseaseAlert(
            disease=disease,
            severity=severity,
            action=actions.get(severity, "Monitor field conditions."),
        )

__all__ = ["DiseaseAlert", "DiseaseAlertGenerator"]
