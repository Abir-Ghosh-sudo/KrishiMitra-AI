from __future__ import annotations
from dataclasses import dataclass

_EMISSION_FACTORS: dict[str, float] = {
    "urea": 1.08, "dap": 0.64, "mop": 0.56,
    "diesel": 2.68, "electricity": 0.82,
}

@dataclass(frozen=True)
class CarbonFootprint:
    total_kg_co2e: float
    breakdown: dict[str, float]

class CarbonCalculator:
    def calculate(self, usage: dict[str, float]) -> CarbonFootprint:
        breakdown = {k: v * _EMISSION_FACTORS.get(k, 1.0) for k, v in usage.items()}
        return CarbonFootprint(sum(breakdown.values()), breakdown)

__all__ = ["CarbonCalculator", "CarbonFootprint"]
