from __future__ import annotations
from .engine import Recommendation

class ConfidenceEstimator:
    def estimate(self, rec: Recommendation, supporting_signals: int = 1) -> float:
        adjusted = rec.confidence * (0.8 + 0.1 * min(supporting_signals, 2))
        return round(min(1.0, adjusted), 3)

__all__ = ["ConfidenceEstimator"]
