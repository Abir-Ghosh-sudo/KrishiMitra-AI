from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IrrigationSimResult:
    total_water_mm: float
    estimated_yield_kg_ha: float
    water_use_efficiency: float

class IrrigationSimulator:
    def simulate(self, et0_list: list[float], kc: float, base_yield: float) -> IrrigationSimResult:
        total = sum(max(0.0, et0 * kc) for et0 in et0_list)
        yield_est = base_yield * min(1.0, total / max(1.0, sum(et0_list)))
        wue = yield_est / total if total > 0 else 0.0
        return IrrigationSimResult(total, round(yield_est, 1), round(wue, 3))

__all__ = ["IrrigationSimResult", "IrrigationSimulator"]
