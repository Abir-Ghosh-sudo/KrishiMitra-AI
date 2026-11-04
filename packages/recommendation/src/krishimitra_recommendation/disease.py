from __future__ import annotations
from .engine import Recommendation

_TREATMENTS: dict[str, str] = {
    "late_blight": "Apply Mancozeb 75WP at 2g/L; repeat every 7 days.",
    "early_blight": "Apply Chlorothalonil 75WP; remove infected leaves.",
    "powdery_mildew": "Apply wettable sulfur or Karathane at recommended dose.",
    "rice_blast": "Apply Tricyclazole 75WP 0.6g/L; drain fields periodically.",
    "downy_mildew": "Apply Metalaxyl+Mancozeb; improve drainage.",
}

class DiseaseRecommender:
    def recommend(self, context: dict) -> list[Recommendation]:
        disease = context.get("disease", "").lower()
        action = _TREATMENTS.get(disease, "Consult an agronomist for diagnosis and treatment.")
        confidence = 0.85 if disease in _TREATMENTS else 0.40
        return [Recommendation(category="disease", action=action, rationale=f"Detected: {disease}", confidence=confidence, priority=3)]

__all__ = ["DiseaseRecommender"]
