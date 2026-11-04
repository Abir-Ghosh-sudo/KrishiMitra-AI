from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PestAlert:
    pest: str
    risk_level: str
    action: str

class PestAlertGenerator:
    def generate(self, pest: str, risk_level: str) -> PestAlert:
        actions = {
            "critical": "Emergency pesticide application required.",
            "high": "Apply targeted pesticide within 24 hours.",
            "moderate": "Increase scouting frequency.",
            "low": "No immediate action; continue monitoring.",
        }
        return PestAlert(
            pest=pest,
            risk_level=risk_level,
            action=actions.get(risk_level, "Monitor field."),
        )

__all__ = ["PestAlert", "PestAlertGenerator"]
