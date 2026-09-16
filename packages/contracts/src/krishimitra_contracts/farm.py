"""Farm service contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FarmStatus(StrEnum):
    """Lifecycle status of a farm."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class FarmContract(BaseModel):
    """Shared representation of a farmer's farm."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    farm_id: UUID
    farmer_id: UUID

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    status: FarmStatus = FarmStatus.ACTIVE

    area_hectares: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=4,
    )

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )

    village: str | None = Field(
        default=None,
        max_length=200,
    )

    district: str | None = Field(
        default=None,
        max_length=200,
    )

    state: str | None = Field(
        default=None,
        max_length=200,
    )

    country: str = Field(
        default="India",
        min_length=1,
        max_length=100,
    )

    created_at: datetime
    updated_at: datetime


class FarmCreateContract(BaseModel):
    """Contract for creating a farm."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    farmer_id: UUID

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    area_hectares: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=4,
    )

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )

    village: str | None = Field(
        default=None,
        max_length=200,
    )

    district: str | None = Field(
        default=None,
        max_length=200,
    )

    state: str | None = Field(
        default=None,
        max_length=200,
    )

    country: str = Field(
        default="India",
        min_length=1,
        max_length=100,
    )


class FarmUpdateContract(BaseModel):
    """Contract for partially updating farm information."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    status: FarmStatus | None = None

    area_hectares: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=4,
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

    village: str | None = Field(
        default=None,
        max_length=200,
    )

    district: str | None = Field(
        default=None,
        max_length=200,
    )

    state: str | None = Field(
        default=None,
        max_length=200,
    )


__all__ = [
    "FarmContract",
    "FarmCreateContract",
    "FarmStatus",
    "FarmUpdateContract",
]