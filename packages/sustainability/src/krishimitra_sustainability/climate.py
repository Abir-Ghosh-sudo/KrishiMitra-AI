from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ClimateRisk:
    drought_risk: str
    flood_risk: str
    heat_stress_risk: str
    overall: str

class ClimateRiskAssessor:
    def assess(self, annual_rain_mm: float, avg_temp_c: float, rainfall_variability: float) -> ClimateRisk:
        drought = "high" if annual_rain_mm < 600 else "moderate" if annual_rain_mm < 900 else "low"
        flood = "high" if annual_rain_mm > 1500 else "moderate" if annual_rain_mm > 1000 else "low"
        heat = "high" if avg_temp_c > 32 else "moderate" if avg_temp_c > 28 else "low"
        risks = [drought, flood, heat]
        overall = "high" if "high" in risks else "moderate" if "moderate" in risks else "low"
        return ClimateRisk(drought, flood, heat, overall)

__all__ = ["ClimateRisk", "ClimateRiskAssessor"]
