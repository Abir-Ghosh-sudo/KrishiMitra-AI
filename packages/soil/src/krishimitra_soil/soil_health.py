from __future__ import annotations
from dataclasses import dataclass
from .nutrient import NutrientProfile

@dataclass(frozen=True)
class SoilHealthIndex:
    score: float  # 0–100
    category: str
    limiting_factors: list[str]

def compute_soil_health(profile: NutrientProfile) -> SoilHealthIndex:
    score = 100.0
    factors: list[str] = []
    if profile.organic_carbon_pct < 0.5:
        score -= 20; factors.append("low_organic_carbon")
    if profile.ph < 5.5 or profile.ph > 8.5:
        score -= 15; factors.append("ph_extreme")
    if profile.nitrogen_kg_ha < 140:
        score -= 15; factors.append("nitrogen_deficient")
    category = "excellent" if score >= 80 else "good" if score >= 60 else "fair" if score >= 40 else "poor"
    return SoilHealthIndex(max(0.0, score), category, factors)

__all__ = ["SoilHealthIndex", "compute_soil_health"]
