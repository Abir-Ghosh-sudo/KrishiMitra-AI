"""WhatsApp integration models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WhatsAppMessageType(StrEnum):
    """Supported WhatsApp message types."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    INTERACTIVE = "interactive"
    UNKNOWN = "unknown"


class WhatsAppMessageStatus(StrEnum):
    """WhatsApp message processing status."""

    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class WhatsAppMessage(BaseModel):
    """Normalized WhatsApp message received by KrishiMitra."""

    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(min_length=1)
    phone_number: str = Field(min_length=1)

    message_type: WhatsAppMessageType

    status: WhatsAppMessageStatus = WhatsAppMessageStatus.RECEIVED

    text: str | None = None

    media_id: str | None = None
    media_url: str | None = None
    mime_type: str | None = None

    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)

    received_at: datetime
    processed_at: datetime | None = None

    raw_payload_hash: str | None = None


class WhatsAppDeliveryStatus(BaseModel):
    """Outbound WhatsApp delivery status."""

    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(min_length=1)
    recipient_phone: str = Field(min_length=1)

    status: WhatsAppMessageStatus

    timestamp: datetime

    provider_message_id: str | None = None

    error_code: str | None = None
    error_message: str | None = None


class WhatsAppConversation(BaseModel):
    """Farmer WhatsApp conversation metadata."""

    model_config = ConfigDict(extra="forbid")

    conversation_id: UUID
    farmer_id: UUID

    phone_number: str = Field(min_length=1)

    started_at: datetime
    last_message_at: datetime | None = None

    preferred_language: str | None = None

    is_active: bool = True


__all__ = [
    "WhatsAppConversation",
    "WhatsAppDeliveryStatus",
    "WhatsAppMessage",
    "WhatsAppMessageStatus",
    "WhatsAppMessageType",
]