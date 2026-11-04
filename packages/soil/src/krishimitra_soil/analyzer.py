from __future__ import annotations
from dataclasses import dataclass
from .nutrient import NutrientProfile

@dataclass(frozen=True)
class SoilAnalysis:
    profile: NutrientProfile
    crop: str
    suitable_for_crop: bool
    notes: list[str]

class SoilAnalyzer:
    _CROP_PH_RANGES: dict[str, tuple[float, float]] = {
        "rice": (5.5, 7.0), "wheat": (6.0, 7.5), "maize": (5.8, 7.0),
        "cotton": (6.0, 7.5), "potato": (5.0, 6.5),
    }

    def analyze(self, profile: NutrientProfile, crop: str) -> SoilAnalysis:
        ph_range = self._CROP_PH_RANGES.get(crop.lower(), (6.0, 7.5))
        suitable = ph_range[0] <= profile.ph <= ph_range[1]
        notes: list[str] = []
        if profile.nitrogen_kg_ha < 140:
            notes.append("Nitrogen deficiency — apply Urea before sowing.")
        if profile.ph < 6.0:
            notes.append("Acidic soil — apply lime at 2 t/ha.")
        elif profile.ph > 8.0:
            notes.append("Alkaline soil — apply gypsum at 250 kg/ha.")
        return SoilAnalysis(profile, crop, suitable, notes)

__all__ = ["SoilAnalysis", "SoilAnalyzer"]
