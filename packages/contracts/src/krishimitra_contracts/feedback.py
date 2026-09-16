"""Feedback service contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackType(StrEnum):
    """Types of feedback that a farmer or expert can provide."""

    RATING = "rating"
    CORRECTION = "correction"
    OUTCOME = "outcome"
    COMMENT = "comment"


class FeedbackSentiment(StrEnum):
    """Optional normalized sentiment of textual feedback."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"


class FeedbackContract(BaseModel):
    """Feedback exchanged between application services."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    feedback_id: UUID

    farmer_id: UUID

    feedback_type: FeedbackType

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=4000,
    )

    sentiment: FeedbackSentiment = FeedbackSentiment.UNKNOWN

    target_type: str = Field(
        min_length=1,
        max_length=100,
    )

    target_id: UUID | None = None

    is_verified: bool = False

    created_at: datetime


class FeedbackCreateContract(BaseModel):
    """Contract for submitting farmer feedback."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    farmer_id: UUID

    feedback_type: FeedbackType

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=4000,
    )

    target_type: str = Field(
        min_length=1,
        max_length=100,
    )

    target_id: UUID | None = None


__all__ = [
    "FeedbackContract",
    "FeedbackCreateContract",
    "FeedbackSentiment",
    "FeedbackType",
]