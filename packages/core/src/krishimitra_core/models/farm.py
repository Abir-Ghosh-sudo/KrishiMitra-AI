"""Farm models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .location import Location


class FarmStatus(StrEnum):
    """Lifecycle status of a farm."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Farm(BaseModel):
    """Core farm representation."""

    model_config = ConfigDict(extra="forbid")

    farm_id: UUID
    farmer_id: UUID

    name: str = Field(min_length=1, max_length=200)
    status: FarmStatus = FarmStatus.ACTIVE

    location: Location

    area_hectares: float = Field(gt=0)
    soil_type: str | None = None
    irrigation_type: str | None = None

    crops: list[str] = Field(default_factory=list)


__all__ = [
    "Farm",
    "FarmStatus",
]