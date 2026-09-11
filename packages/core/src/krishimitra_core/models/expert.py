"""Expert escalation and review models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExpertReviewStatus(StrEnum):
    """Lifecycle status of an expert review."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ExpertReviewPriority(StrEnum):
    """Priority of an expert review request."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExpertReviewRequest(BaseModel):
    """Request created when AI confidence is insufficient."""

    model_config = ConfigDict(extra="forbid")

    review_id: UUID

    farmer_id: UUID
    farm_id: UUID | None = None
    crop_id: UUID | None = None

    message_id: str | None = None
    diagnosis_id: UUID | None = None
    recommendation_id: UUID | None = None

    priority: ExpertReviewPriority = ExpertReviewPriority.MEDIUM
    status: ExpertReviewStatus = ExpertReviewStatus.PENDING

    reason: str = Field(min_length=1, max_length=2000)

    ai_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime
    assigned_at: datetime | None = None
    completed_at: datetime | None = None


class ExpertReview(BaseModel):
    """Verified expert assessment returned to the AI workflow."""

    model_config = ConfigDict(extra="forbid")

    review_id: UUID
    expert_id: UUID

    status: ExpertReviewStatus = ExpertReviewStatus.COMPLETED

    diagnosis: str | None = Field(default=None, max_length=500)
    recommendation: str | None = Field(default=None, max_length=5000)

    notes: str | None = Field(default=None, max_length=5000)

    verified: bool = False

    reviewed_at: datetime

    evidence: list[str] = Field(default_factory=list)


__all__ = [
    "ExpertReview",
    "ExpertReviewPriority",
    "ExpertReviewRequest",
    "ExpertReviewStatus",
]