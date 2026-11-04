from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

class NutrientStatus(StrEnum):
    DEFICIENT = "deficient"
    LOW = "low"
    ADEQUATE = "adequate"
    HIGH = "high"
    TOXIC = "toxic"

@dataclass(frozen=True)
class NutrientProfile:
    nitrogen_kg_ha: float
    phosphorus_kg_ha: float
    potassium_kg_ha: float
    organic_carbon_pct: float
    ph: float

    @property
    def nitrogen_status(self) -> NutrientStatus:
        if self.nitrogen_kg_ha < 140: return NutrientStatus.DEFICIENT
        if self.nitrogen_kg_ha < 280: return NutrientStatus.LOW
        if self.nitrogen_kg_ha < 420: return NutrientStatus.ADEQUATE
        return NutrientStatus.HIGH

    @property
    def ph_status(self) -> str:
        if self.ph < 5.5: return "strongly_acidic"
        if self.ph < 6.5: return "slightly_acidic"
        if self.ph <= 7.5: return "neutral"
        if self.ph <= 8.5: return "alkaline"
        return "strongly_alkaline"

__all__ = ["NutrientProfile", "NutrientStatus"]
