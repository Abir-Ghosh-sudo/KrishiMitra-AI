from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class FertilizerSimResult:
    n_applied_kg: float
    p_applied_kg: float
    k_applied_kg: float
    estimated_yield_increase_pct: float

class FertilizerSimulator:
    def simulate(self, n: float, p: float, k: float) -> FertilizerSimResult:
        gain = min(40.0, (n * 0.3 + p * 0.2 + k * 0.1))
        return FertilizerSimResult(n, p, k, round(gain, 1))

__all__ = ["FertilizerSimResult", "FertilizerSimulator"]
