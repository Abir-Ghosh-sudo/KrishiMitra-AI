from __future__ import annotations

from dataclasses import dataclass


class ConfidenceError(ValueError):
    """Raised when confidence data is invalid."""


@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    """Normalized confidence assessment for a vision prediction."""

    score: float
    accepted: bool
    needs_review: bool
    level: str


class ConfidenceEvaluator:
    """Evaluate model confidence and determine whether review is required."""

    def __init__(
        self,
        *,
        acceptance_threshold: float = 0.75,
        review_threshold: float = 0.50,
    ) -> None:
        if not 0.0 <= review_threshold <= 1.0:
            raise ValueError(
                "review_threshold must be between 0 and 1"
            )

        if not 0.0 <= acceptance_threshold <= 1.0:
            raise ValueError(
                "acceptance_threshold must be between 0 and 1"
            )

        if review_threshold > acceptance_threshold:
            raise ValueError(
                "review_threshold cannot exceed acceptance_threshold"
            )

        self._acceptance_threshold = acceptance_threshold
        self._review_threshold = review_threshold

    def evaluate(self, score: float) -> ConfidenceResult:
        """Evaluate a model confidence score."""

        if not 0.0 <= score <= 1.0:
            raise ConfidenceError(
                "confidence score must be between 0 and 1"
            )

        if score >= self._acceptance_threshold:
            return ConfidenceResult(
                score=score,
                accepted=True,
                needs_review=False,
                level="high",
            )

        if score >= self._review_threshold:
            return ConfidenceResult(
                score=score,
                accepted=False,
                needs_review=True,
                level="medium",
            )

        return ConfidenceResult(
            score=score,
            accepted=False,
            needs_review=True,
            level="low",
        )


__all__ = [
    "ConfidenceError",
    "ConfidenceEvaluator",
    "ConfidenceResult",
]