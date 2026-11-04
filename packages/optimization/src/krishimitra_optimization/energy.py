from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EnergyPlan:
    pump_hours: float
    off_peak_hours: float
    estimated_cost: float

class EnergyOptimizer:
    def optimize(self, water_mm: float, pump_kw: float, tariff_peak: float, tariff_offpeak: float) -> EnergyPlan:
        total_kwh = water_mm * pump_kw / 10.0
        off_peak = total_kwh * 0.7
        peak = total_kwh * 0.3
        cost = off_peak * tariff_offpeak + peak * tariff_peak
        return EnergyPlan(pump_hours=total_kwh / pump_kw, off_peak_hours=off_peak / pump_kw, estimated_cost=round(cost, 2))

__all__ = ["EnergyOptimizer", "EnergyPlan"]
