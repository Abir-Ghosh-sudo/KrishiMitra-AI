from __future__ import annotations

class ConfidenceGate:
    def __init__(self, threshold: float = 0.65) -> None:
        self._threshold = threshold

    def allows(self, confidence: float) -> bool:
        return confidence >= self._threshold

    def requires_human_review(self, confidence: float) -> bool:
        return confidence < self._threshold * 0.7

__all__ = ["ConfidenceGate"]
