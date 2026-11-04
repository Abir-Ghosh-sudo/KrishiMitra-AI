from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SustainabilityScore:
    water_score: float
    chemical_score: float
    carbon_score: float
    overall: float

class SustainabilityOptimizer:
    def score(self, water_use: float, chemical_apps: int, fossil_kwh: float) -> SustainabilityScore:
        w = max(0.0, 100.0 - water_use / 10)
        c = max(0.0, 100.0 - chemical_apps * 10)
        f = max(0.0, 100.0 - fossil_kwh)
        return SustainabilityScore(w, c, f, round((w + c + f) / 3, 1))

__all__ = ["SustainabilityOptimizer", "SustainabilityScore"]
