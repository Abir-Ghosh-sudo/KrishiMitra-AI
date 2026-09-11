
"""Confidence and uncertainty models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConfidenceLevel(StrEnum):
    """Human-readable confidence levels."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ConfidenceScore(BaseModel):
    """Validated confidence score for an AI/ML result."""

    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0, le=1.0)
    level: ConfidenceLevel

    @model_validator(mode="after")
    def validate_level(self) -> "ConfidenceScore":
        """Ensure the confidence level matches the numeric score."""
        expected = self.level_for_score(self.score)

        if self.level != expected:
            raise ValueError(
                f"confidence level '{self.level}' does not match "
                f"score {self.score:.3f}; expected '{expected}'"
            )

        return self

    @staticmethod
    def level_for_score(score: float) -> ConfidenceLevel:
        """Map a normalized score to a confidence level."""
        if score < 0.20:
            return ConfidenceLevel.VERY_LOW
        if score < 0.40:
            return ConfidenceLevel.LOW
        if score < 0.60:
            return ConfidenceLevel.MEDIUM
        if score < 0.80:
            return ConfidenceLevel.HIGH
        return ConfidenceLevel.VERY_HIGH

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceScore":
        """Create a confidence score with its derived level."""
        return cls(
            score=score,
            level=cls.level_for_score(score),
        )


class Uncertainty(BaseModel):
    """Represent uncertainty associated with a model prediction."""

    model_config = ConfigDict(extra="forbid")

    lower_bound: float | None = None
    upper_bound: float | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def validate_bounds(self) -> "Uncertainty":
        """Ensure uncertainty bounds are logically ordered."""
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self.lower_bound > self.upper_bound
        ):
            raise ValueError("lower_bound cannot be greater than upper_bound")

        return self


__all__ = [
    "ConfidenceLevel",
    "ConfidenceScore",
    "Uncertainty",
]