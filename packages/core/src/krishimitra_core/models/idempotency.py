"""Idempotency models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IdempotencyStatus(StrEnum):
    """Lifecycle status of an idempotent operation."""

    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class IdempotencyRecord(BaseModel):
    """Persistent record used to prevent duplicate request processing."""

    model_config = ConfigDict(extra="forbid")

    record_id: UUID

    idempotency_key: str = Field(min_length=1, max_length=512)

    operation: str = Field(min_length=1, max_length=200)

    status: IdempotencyStatus = IdempotencyStatus.RECEIVED

    request_hash: str | None = Field(default=None, max_length=128)

    response_reference: str | None = Field(default=None, max_length=500)

    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None

    retry_count: int = Field(default=0, ge=0)

    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = Field(default=None, max_length=2000)


__all__ = [
    "IdempotencyRecord",
    "IdempotencyStatus",
]
