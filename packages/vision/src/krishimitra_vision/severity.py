from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SeverityLevel(StrEnum):
    """Standardized plant-damage severity levels."""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SeverityEstimationError(ValueError):
    """Raised when severity estimation input is invalid."""


@dataclass(frozen=True, slots=True)
class SeverityResult:
    """Estimated severity of visible plant damage."""

    level: SeverityLevel
    score: float
    affected_ratio: float


class SeverityEstimator:
    """
    Estimate visible damage severity from an affected-area ratio.

    The ratio is expected to represent the proportion of the relevant
    plant area showing visible symptoms. This is a visual estimate,
    not a complete agronomic assessment.
    """

    def __init__(
        self,
        *,
        low_threshold: float = 0.10,
        moderate_threshold: float = 0.30,
        high_threshold: float = 0.60,
        critical_threshold: float = 0.85,
    ) -> None:
        thresholds = (
            low_threshold,
            moderate_threshold,
            high_threshold,
            critical_threshold,
        )

        if any(not 0.0 <= value <= 1.0 for value in thresholds):
            raise ValueError("severity thresholds must be between 0 and 1")

        if not (
            low_threshold
            <= moderate_threshold
            <= high_threshold
            <= critical_threshold
        ):
            raise ValueError(
                "severity thresholds must be monotonically increasing"
            )

        self._low = low_threshold
        self._moderate = moderate_threshold
        self._high = high_threshold
        self._critical = critical_threshold

    def estimate(self, affected_ratio: float) -> SeverityResult:
        """Estimate severity from an affected-area ratio."""

        if not 0.0 <= affected_ratio <= 1.0:
            raise SeverityEstimationError(
                "affected_ratio must be between 0 and 1"
            )

        if affected_ratio == 0.0:
            level = SeverityLevel.NONE
        elif affected_ratio < self._low:
            level = SeverityLevel.LOW
        elif affected_ratio < self._moderate:
            level = SeverityLevel.MODERATE
        elif affected_ratio < self._high:
            level = SeverityLevel.HIGH
        else:
            level = SeverityLevel.CRITICAL

        return SeverityResult(
            level=level,
            score=affected_ratio,
            affected_ratio=affected_ratio,
        )


__all__ = [
    "SeverityEstimationError",
    "SeverityEstimator",
    "SeverityLevel",
    "SeverityResult",
]