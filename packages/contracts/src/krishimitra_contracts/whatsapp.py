"""WhatsApp service contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WhatsAppMessageType(StrEnum):
    """Supported inbound and outbound WhatsApp message types."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    INTERACTIVE = "interactive"
    UNKNOWN = "unknown"


class WhatsAppMessageDirection(StrEnum):
    """Direction of a WhatsApp message."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


class WhatsAppMessageStatus(StrEnum):
    """Processing and delivery status of a WhatsApp message."""

    RECEIVED = "received"
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class WhatsAppMessageContract(BaseModel):
    """Shared WhatsApp message representation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    message_id: UUID

    farmer_id: UUID | None = None

    provider_message_id: str = Field(
        min_length=1,
        max_length=200,
    )

    phone_number: str = Field(
        min_length=5,
        max_length=30,
    )

    direction: WhatsAppMessageDirection

    message_type: WhatsAppMessageType

    status: WhatsAppMessageStatus = WhatsAppMessageStatus.RECEIVED

    text: str | None = Field(
        default=None,
        max_length=10000,
    )

    media_url: str | None = Field(
        default=None,
        max_length=2000,
    )

    mime_type: str | None = Field(
        default=None,
        max_length=200,
    )

    media_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    received_at: datetime

    processed_at: datetime | None = None


class WhatsAppInboundContract(BaseModel):
    """Contract for an inbound WhatsApp message entering the system."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    provider_message_id: str = Field(
        min_length=1,
        max_length=200,
    )

    phone_number: str = Field(
        min_length=5,
        max_length=30,
    )

    message_type: WhatsAppMessageType

    text: str | None = Field(
        default=None,
        max_length=10000,
    )

    media_url: str | None = Field(
        default=None,
        max_length=2000,
    )

    mime_type: str | None = Field(
        default=None,
        max_length=200,
    )

    media_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    received_at: datetime


class WhatsAppOutboundContract(BaseModel):
    """Contract for sending a WhatsApp response to a farmer."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    farmer_id: UUID | None = None

    phone_number: str = Field(
        min_length=5,
        max_length=30,
    )

    message_type: WhatsAppMessageType = WhatsAppMessageType.TEXT

    text: str | None = Field(
        default=None,
        max_length=10000,
    )

    media_url: str | None = Field(
        default=None,
        max_length=2000,
    )

    mime_type: str | None = Field(
        default=None,
        max_length=200,
    )

    media_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    reply_to_message_id: str | None = Field(
        default=None,
        max_length=200,
    )


__all__ = [
    "WhatsAppInboundContract",
    "WhatsAppMessageContract",
    "WhatsAppMessageDirection",
    "WhatsAppMessageStatus",
    "WhatsAppMessageType",
    "WhatsAppOutboundContract",
]