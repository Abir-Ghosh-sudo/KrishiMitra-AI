"""Message models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from .language import LanguageCode
from .media import MediaReference


class MessageDirection(StrEnum):
    """Message direction."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageType(StrEnum):
    """Supported message types."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    INTERACTIVE = "interactive"


class MessageStatus(StrEnum):
    """Message processing/delivery status."""

    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(BaseModel):
    """Normalized application-level message."""

    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(min_length=1)
    direction: MessageDirection
    message_type: MessageType
    status: MessageStatus = MessageStatus.RECEIVED

    sender_id: str | None = None
    conversation_id: str | None = None

    text: str | None = None
    language: LanguageCode | None = None

    media: list[MediaReference] = Field(default_factory=list)

    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)

    created_at: datetime
    processed_at: datetime | None = None


__all__ = [
    "Message",
    "MessageDirection",
    "MessageStatus",
    "MessageType",
]