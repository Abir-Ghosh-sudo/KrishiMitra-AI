from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SustainabilityAlert:
    metric: str
    value: float
    threshold: float
    recommendation: str

class SustainabilityAlertGenerator:
    def check_water_overuse(self, used_mm: float, budget_mm: float) -> SustainabilityAlert | None:
        if used_mm > budget_mm:
            return SustainabilityAlert(
                metric="water_use",
                value=used_mm,
                threshold=budget_mm,
                recommendation="Reduce irrigation volume; consider drip irrigation.",
            )
        return None

    def check_chemical_load(self, applications: int, limit: int) -> SustainabilityAlert | None:
        if applications > limit:
            return SustainabilityAlert(
                metric="chemical_applications",
                value=float(applications),
                threshold=float(limit),
                recommendation="Reduce pesticide applications; use IPM strategies.",
            )
        return None

__all__ = ["SustainabilityAlert", "SustainabilityAlertGenerator"]
