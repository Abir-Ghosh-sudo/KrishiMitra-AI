from __future__ import annotations
from dataclasses import dataclass
from .trends import TrendDirection, PriceTrend

@dataclass(frozen=True)
class MarketRecommendation:
    commodity: str
    action: str
    rationale: str
    confidence: float

class MarketAdvisor:
    def advise(self, trend: PriceTrend) -> MarketRecommendation:
        if trend.direction == TrendDirection.RISING:
            action, rationale = "hold", "Prices are rising — hold stock if storage is available."
        elif trend.direction == TrendDirection.FALLING:
            action, rationale = "sell", "Prices are falling — consider selling now to avoid further losses."
        else:
            action, rationale = "sell_partial", "Prices are stable — sell a portion and retain rest."
        return MarketRecommendation(
            commodity=trend.commodity, action=action,
            rationale=rationale, confidence=0.7,
        )

__all__ = ["MarketAdvisor", "MarketRecommendation"]
