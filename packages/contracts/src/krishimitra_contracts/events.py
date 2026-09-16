"""Event contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventType(StrEnum):
    """Types of domain and integration events."""

    WHATSAPP_MESSAGE_RECEIVED = "whatsapp.message_received"
    WHATSAPP_MESSAGE_PROCESSED = "whatsapp.message_processed"

    DIAGNOSIS_CREATED = "diagnosis.created"
    RECOMMENDATION_CREATED = "recommendation.created"

    ALERT_CREATED = "alert.created"
    ALERT_SENT = "alert.sent"

    FARM_CREATED = "farm.created"
    FARM_UPDATED = "farm.updated"

    FEEDBACK_RECEIVED = "feedback.received"

    PREDICTION_CREATED = "prediction.created"

    DOCUMENT_PROCESSED = "document.processed"


class EventMetadata(BaseModel):
    """Metadata used for tracing and event processing."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    request_id: UUID | None = None
    correlation_id: UUID | None = None

    producer: str = Field(
        min_length=1,
        max_length=100,
    )

    schema_version: str = Field(
        default="1.0",
        min_length=1,
        max_length=20,
    )


class DomainEvent(BaseModel):
    """Generic event envelope shared between KrishiMitra services."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    event_id: UUID

    event_type: EventType

    aggregate_id: UUID | None = None

    occurred_at: datetime

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: EventMetadata

    sequence: int | None = Field(
        default=None,
        ge=0,
    )


__all__ = [
    "DomainEvent",
    "EventMetadata",
    "EventType",
]