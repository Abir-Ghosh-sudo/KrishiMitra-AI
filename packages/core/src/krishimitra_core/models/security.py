"""Security and access-control models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserRole(StrEnum):
    """Application roles."""

    FARMER = "farmer"
    EXPERT = "expert"
    ADMIN = "admin"
    SERVICE = "service"


class AccountStatus(StrEnum):
    """User account lifecycle status."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"
    PENDING = "pending"


class UserAccount(BaseModel):
    """Application user identity and authorization metadata."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID

    role: UserRole
    status: AccountStatus = AccountStatus.ACTIVE

    phone_number: str | None = None
    email: str | None = None

    created_at: datetime
    last_login_at: datetime | None = None

    is_verified: bool = False


class Permission(BaseModel):
    """Fine-grained application permission."""

    model_config = ConfigDict(extra="forbid")

    permission: str = Field(min_length=1, max_length=200)
    description: str | None = None


class AccessTokenMetadata(BaseModel):
    """Metadata associated with an authenticated access token."""

    model_config = ConfigDict(extra="forbid")

    subject_id: UUID
    role: UserRole

    issued_at: datetime
    expires_at: datetime

    token_id: str = Field(min_length=1)

    scopes: list[str] = Field(default_factory=list)


__all__ = [
    "AccessTokenMetadata",
    "AccountStatus",
    "Permission",
    "UserAccount",
    "UserRole",
]