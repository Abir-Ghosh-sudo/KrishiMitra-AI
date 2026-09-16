"""Farmer service contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FarmerStatus(StrEnum):
    """Lifecycle status of a farmer account."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class FarmerContract(BaseModel):
    """Shared representation of a farmer identity."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    farmer_id: UUID

    status: FarmerStatus = FarmerStatus.ACTIVE

    display_name: str | None = Field(
        default=None,
        max_length=200,
    )

    phone_number: str = Field(
        min_length=5,
        max_length=30,
    )

    preferred_language: str = Field(
        default="en",
        min_length=2,
        max_length=20,
    )

    timezone: str = Field(
        default="Asia/Kolkata",
        min_length=1,
        max_length=100,
    )

    is_verified: bool = False

    created_at: datetime
    updated_at: datetime
    last_active_at: datetime | None = None


class FarmerCreateContract(BaseModel):
    """Contract for creating a farmer profile."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    phone_number: str = Field(
        min_length=5,
        max_length=30,
    )

    display_name: str | None = Field(
        default=None,
        max_length=200,
    )

    preferred_language: str = Field(
        default="en",
        min_length=2,
        max_length=20,
    )

    timezone: str = Field(
        default="Asia/Kolkata",
        min_length=1,
        max_length=100,
    )


class FarmerUpdateContract(BaseModel):
    """Contract for updating farmer preferences and profile data."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    display_name: str | None = Field(
        default=None,
        max_length=200,
    )

    preferred_language: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    status: FarmerStatus | None = None


__all__ = [
    "FarmerContract",
    "FarmerCreateContract",
    "FarmerStatus",
    "FarmerUpdateContract",
]