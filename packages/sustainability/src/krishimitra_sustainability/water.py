from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class WaterFootprint:
    blue_water_m3: float
    green_water_m3: float
    total_m3: float

class WaterFootprintCalculator:
    def calculate(self, irrigation_mm: float, rainfall_mm: float, area_ha: float) -> WaterFootprint:
        blue = irrigation_mm * area_ha * 10
        green = rainfall_mm * area_ha * 10
        return WaterFootprint(blue, green, blue + green)

__all__ = ["WaterFootprint", "WaterFootprintCalculator"]
