from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Recommendation:
    category: str
    action: str
    rationale: str
    confidence: float
    priority: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

class RecommendationEngine:
    def __init__(self) -> None:
        self._recommenders: list[Any] = []

    def register(self, recommender: Any) -> None:
        self._recommenders.append(recommender)

    def generate(self, context: dict[str, Any]) -> list[Recommendation]:
        results: list[Recommendation] = []
        for r in self._recommenders:
            if hasattr(r, "recommend"):
                try:
                    recs = r.recommend(context)
                    if isinstance(recs, list):
                        results.extend(recs)
                except Exception:
                    pass
        return sorted(results, key=lambda r: -r.priority)

__all__ = ["Recommendation", "RecommendationEngine"]
