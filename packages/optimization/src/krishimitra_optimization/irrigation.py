from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IrrigationSchedule:
    field_id: str
    daily_allocation_mm: list[float]
    total_mm: float
    efficiency_pct: float

class IrrigationOptimizer:
    def optimize(
        self,
        et0_list: list[float],
        kc: float,
        rain_list: list[float],
        efficiency: float = 0.85,
    ) -> IrrigationSchedule:
        allocations = [
            max(0.0, round((et0 * kc - rain) / efficiency, 1))
            for et0, rain in zip(et0_list, rain_list)
        ]
        return IrrigationSchedule(
            field_id="default",
            daily_allocation_mm=allocations,
            total_mm=sum(allocations),
            efficiency_pct=efficiency * 100,
        )

__all__ = ["IrrigationOptimizer", "IrrigationSchedule"]
