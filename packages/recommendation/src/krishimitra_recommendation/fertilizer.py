from __future__ import annotations
from .engine import Recommendation

class FertilizerRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        crop = context.get("crop", "unknown")
        n = context.get("n_deficiency", False)
        p = context.get("p_deficiency", False)
        k = context.get("k_deficiency", False)
        actions = []
        if n: actions.append("Apply Urea (46%N) at 50kg/acre in split doses.")
        if p: actions.append("Apply DAP (18%N, 46%P2O5) at 25kg/acre as basal.")
        if k: actions.append("Apply MOP (60%K2O) at 20kg/acre.")
        if not actions: actions.append("Soil nutrients are adequate; continue monitoring.")
        return [Recommendation(category="fertilizer", action="; ".join(actions),
                               rationale=f"Based on soil test for {crop}", confidence=0.80, priority=2)]

__all__ = ["FertilizerRecommender"]
