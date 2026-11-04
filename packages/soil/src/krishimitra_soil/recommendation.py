from __future__ import annotations
from dataclasses import dataclass
from .nutrient import NutrientProfile, NutrientStatus

@dataclass(frozen=True)
class SoilRecommendation:
    crop: str
    urea_kg_ha: float
    dap_kg_ha: float
    mop_kg_ha: float
    lime_kg_ha: float
    notes: list[str]

class SoilRecommender:
    def recommend(self, profile: NutrientProfile, crop: str) -> SoilRecommendation:
        urea = 120 if profile.nitrogen_status in (NutrientStatus.DEFICIENT, NutrientStatus.LOW) else 60
        dap = 50 if profile.phosphorus_kg_ha < 20 else 25
        mop = 40 if profile.potassium_kg_ha < 120 else 20
        lime = 2000 if profile.ph < 5.5 else 0
        notes: list[str] = []
        if lime:
            notes.append("Apply lime 4 weeks before sowing.")
        return SoilRecommendation(crop, urea, dap, mop, lime, notes)

__all__ = ["SoilRecommendation", "SoilRecommender"]
