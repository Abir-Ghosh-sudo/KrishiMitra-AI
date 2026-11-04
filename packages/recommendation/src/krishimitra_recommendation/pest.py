from __future__ import annotations
from .engine import Recommendation

_PEST_ACTIONS: dict[str, str] = {
    "aphids": "Spray neem oil (5ml/L) or imidacloprid 0.3ml/L.",
    "whitefly": "Apply buprofezin 25SC; use yellow sticky traps.",
    "fall_armyworm": "Apply emamectin benzoate 5SG 0.4g/L at early stage.",
    "thrips": "Apply spinosad 45SC 0.3ml/L; use blue sticky traps.",
}

class PestRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        pest = context.get("pest", "").lower()
        action = _PEST_ACTIONS.get(pest, "Scout field and consult an entomologist.")
        confidence = 0.80 if pest in _PEST_ACTIONS else 0.45
        return [Recommendation(category="pest", action=action, rationale=f"Pest: {pest}", confidence=confidence, priority=3)]

__all__ = ["PestRecommender"]
