from __future__ import annotations
import re
from .nutrient import NutrientProfile

class SoilReportParser:
    """Parses simple key:value soil test reports."""
    def parse(self, text: str) -> NutrientProfile:
        def extract(key: str, default: float) -> float:
            m = re.search(rf'{key}\s*[:=]\s*([\d.]+)', text, re.IGNORECASE)
            return float(m.group(1)) if m else default

        return NutrientProfile(
            nitrogen_kg_ha=extract("nitrogen", 200),
            phosphorus_kg_ha=extract("phosphorus", 25),
            potassium_kg_ha=extract("potassium", 200),
            organic_carbon_pct=extract("organic.carbon", 0.5),
            ph=extract("ph", 7.0),
        )

__all__ = ["SoilReportParser"]
