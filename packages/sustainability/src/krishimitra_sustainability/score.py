from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SustainabilityReport:
    carbon_score: float
    water_score: float
    chemical_score: float
    energy_score: float
    overall: float
    grade: str

class SustainabilityScorer:
    def score(self, carbon_kg: float, water_m3: float, chemical_apps: int, renewable_frac: float) -> SustainabilityReport:
        c = max(0.0, 100 - carbon_kg / 10)
        w = max(0.0, 100 - water_m3 / 100)
        ch = max(0.0, 100 - chemical_apps * 10)
        e = renewable_frac * 100
        overall = round((c + w + ch + e) / 4, 1)
        grade = "A" if overall >= 80 else "B" if overall >= 60 else "C" if overall >= 40 else "D"
        return SustainabilityReport(c, w, ch, e, overall, grade)

__all__ = ["SustainabilityReport", "SustainabilityScorer"]
