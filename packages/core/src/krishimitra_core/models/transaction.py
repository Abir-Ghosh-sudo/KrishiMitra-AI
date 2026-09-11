"""Transaction models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TransactionStatus(StrEnum):
    """Lifecycle state of an application transaction."""

    STARTED = "started"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class TransactionContext(BaseModel):
    """Context describing a database or application transaction."""

    model_config = ConfigDict(extra="forbid")

    transaction_id: UUID

    status: TransactionStatus = TransactionStatus.STARTED

    started_at: datetime
    completed_at: datetime | None = None

    operation: str = Field(min_length=1, max_length=200)

    request_id: UUID | None = None

    retry_count: int = Field(default=0, ge=0)

    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = Field(default=None, max_length=2000)


__all__ = [
    "TransactionContext",
    "TransactionStatus",
]