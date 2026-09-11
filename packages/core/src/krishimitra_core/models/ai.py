"""AI orchestration models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .confidence import ConfidenceScore


class AIResponseType(StrEnum):
    """Types of AI-generated responses."""

    ANSWER = "answer"
    DIAGNOSIS = "diagnosis"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    CLARIFICATION = "clarification"
    EXPERT_ESCALATION = "expert_escalation"


class AIProcessingStatus(StrEnum):
    """AI request processing status."""

    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class AIInput(BaseModel):
    """Normalized input passed to the AI orchestrator."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID

    farmer_id: UUID | None = None
    farm_id: UUID | None = None
    crop_id: UUID | None = None

    text: str | None = Field(default=None, max_length=10000)

    media_ids: list[str] = Field(default_factory=list)

    language: str | None = None

    context: dict[str, str] = Field(default_factory=dict)


class AIResponse(BaseModel):
    """Structured response produced by the AI orchestration layer."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID

    status: AIProcessingStatus
    response_type: AIResponseType

    message: str = Field(min_length=1, max_length=20000)

    confidence: ConfidenceScore

    grounded: bool = False

    citations: list[str] = Field(default_factory=list)
    contributing_factors: list[str] = Field(default_factory=list)

    requires_expert_review: bool = False

    model_name: str = Field(min_length=1, max_length=200)
    model_version: str = Field(min_length=1, max_length=100)


__all__ = [
    "AIInput",
    "AIProcessingStatus",
    "AIResponse",
    "AIResponseType",
]