from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

class TrendDirection(StrEnum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"

@dataclass(frozen=True)
class PriceTrend:
    commodity: str
    direction: TrendDirection
    change_pct: float
    days_analyzed: int

class TrendAnalyzer:
    def analyze(self, prices: list[float]) -> PriceTrend:
        if len(prices) < 2:
            return PriceTrend("unknown", TrendDirection.STABLE, 0.0, len(prices))
        change = (prices[-1] - prices[0]) / prices[0] * 100
        direction = TrendDirection.RISING if change > 2 else (TrendDirection.FALLING if change < -2 else TrendDirection.STABLE)
        return PriceTrend("unknown", direction, round(change, 2), len(prices))

__all__ = ["PriceTrend", "TrendAnalyzer", "TrendDirection"]
