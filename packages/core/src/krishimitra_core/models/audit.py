"""Audit logging models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditAction(StrEnum):
    """Actions recorded in the audit trail."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PROCESS = "process"
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    SEND = "send"


class AuditActorType(StrEnum):
    """Types of actors that can perform an action."""

    FARMER = "farmer"
    EXPERT = "expert"
    ADMIN = "admin"
    SYSTEM = "system"
    SERVICE = "service"


class AuditEvent(BaseModel):
    """Immutable audit event representing a security-relevant action."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID

    actor_id: UUID | None = None
    actor_type: AuditActorType = AuditActorType.SYSTEM

    action: AuditAction

    resource_type: str = Field(min_length=1, max_length=100)
    resource_id: str | None = None

    timestamp: datetime

    request_id: str | None = None
    ip_address: str | None = None

    success: bool = True

    details: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "AuditAction",
    "AuditActorType",
    "AuditEvent",
]