from __future__ import annotations
from .engine import Recommendation

class IrrigationRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        deficit = context.get("water_deficit_mm", 0.0)
        if deficit <= 0:
            return [Recommendation(category="irrigation", action="No irrigation needed.", rationale="Soil moisture adequate.", confidence=0.90, priority=1)]
        return [Recommendation(category="irrigation", action=f"Apply {deficit:.0f} mm irrigation in early morning.",
                               rationale="Soil moisture deficit detected.", confidence=0.85, priority=2)]

__all__ = ["IrrigationRecommender"]
