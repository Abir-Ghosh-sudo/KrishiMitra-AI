from __future__ import annotations
from .engine import Recommendation

class SprayRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        best_window = context.get("best_spray_window", None)
        if not best_window:
            return [Recommendation(category="spray", action="No suitable spray window found in next 24h.", rationale="Conditions unfavourable.", confidence=0.75, priority=1)]
        return [Recommendation(category="spray", action=f"Spray at {best_window} — low wind, optimal humidity.",
                               rationale="Spray window analysis.", confidence=0.90, priority=2)]

__all__ = ["SprayRecommender"]
