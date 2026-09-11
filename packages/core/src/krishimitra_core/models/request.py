"""Request context models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequestSource(StrEnum):
    """Sources from which an application request can originate."""

    WHATSAPP = "whatsapp"
    API = "api"
    WORKER = "worker"
    SCHEDULER = "scheduler"
    ADMIN = "admin"
    SYSTEM = "system"


class RequestContext(BaseModel):
    """Context propagated across API, worker, and service boundaries."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    correlation_id: UUID | None = None

    source: RequestSource

    operation: str = Field(min_length=1, max_length=200)

    started_at: datetime
    completed_at: datetime | None = None

    actor_id: UUID | None = None

    trace_id: str | None = Field(default=None, max_length=128)

    metadata: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "RequestContext",
    "RequestSource",
]