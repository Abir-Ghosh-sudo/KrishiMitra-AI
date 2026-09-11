"""Notification models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationChannel(StrEnum):
    """Supported notification delivery channels."""

    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    IN_APP = "in_app"


class NotificationStatus(StrEnum):
    """Notification delivery status."""

    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Notification(BaseModel):
    """Notification intended for a farmer or internal user."""

    model_config = ConfigDict(extra="forbid")

    notification_id: UUID

    recipient_id: UUID
    farm_id: UUID | None = None

    channel: NotificationChannel
    status: NotificationStatus = NotificationStatus.PENDING

    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=10000)

    priority: int = Field(default=3, ge=1, le=5)

    scheduled_at: datetime | None = None
    created_at: datetime

    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None

    external_message_id: str | None = None

    retry_count: int = Field(default=0, ge=0)
    failure_reason: str | None = None


__all__ = [
    "Notification",
    "NotificationChannel",
    "NotificationStatus",
]