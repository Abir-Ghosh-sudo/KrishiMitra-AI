from __future__ import annotations
from .collector import FeedbackCollector, Rating

class FeedbackEvaluator:
    def __init__(self, collector: FeedbackCollector) -> None:
        self._collector = collector

    def satisfaction_score(self) -> float:
        records = self._collector.all()
        if not records:
            return 0.0
        positive = sum(1 for r in records if r.rating >= Rating.GOOD)
        return positive / len(records)

    def needs_improvement(self) -> bool:
        return self.satisfaction_score() < 0.7

__all__ = ["FeedbackEvaluator"]
