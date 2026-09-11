"""Feedback and outcome-learning models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackType(StrEnum):
    """Types of farmer or expert feedback."""

    HELPFULNESS = "helpfulness"
    CORRECTION = "correction"
    OUTCOME = "outcome"
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"


class FeedbackRating(StrEnum):
    """Simple feedback rating values."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Feedback(BaseModel):
    """Feedback associated with an AI interaction."""

    model_config = ConfigDict(extra="forbid")

    feedback_id: UUID

    farmer_id: UUID
    farm_id: UUID | None = None
    message_id: str | None = None
    recommendation_id: UUID | None = None
    diagnosis_id: UUID | None = None

    feedback_type: FeedbackType
    rating: FeedbackRating | None = None

    comment: str | None = Field(default=None, max_length=5000)

    corrected_value: str | None = Field(
        default=None,
        max_length=5000,
    )

    created_at: datetime


class OutcomeRecord(BaseModel):
    """Observed real-world outcome used for model improvement."""

    model_config = ConfigDict(extra="forbid")

    outcome_id: UUID

    farmer_id: UUID
    farm_id: UUID

    recommendation_id: UUID | None = None
    diagnosis_id: UUID | None = None

    outcome: str = Field(min_length=1, max_length=2000)

    success: bool | None = None

    observed_at: datetime

    evidence: list[str] = Field(default_factory=list)

    notes: str | None = Field(default=None, max_length=5000)


__all__ = [
    "Feedback",
    "FeedbackRating",
    "FeedbackType",
    "OutcomeRecord",
]