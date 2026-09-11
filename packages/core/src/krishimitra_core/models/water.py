"""Water management and footprint models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WaterSource(StrEnum):
    """Sources of water used by a farm."""

    RAINWATER = "rainwater"
    GROUNDWATER = "groundwater"
    CANAL = "canal"
    RIVER = "river"
    RESERVOIR = "reservoir"
    MUNICIPAL = "municipal"
    OTHER = "other"


class WaterUseRecord(BaseModel):
    """Recorded water consumption for a farm operation."""

    model_config = ConfigDict(extra="forbid")

    record_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    recorded_at: datetime

    source: WaterSource
    volume_liters: float = Field(ge=0.0)

    operation: str = Field(min_length=1, max_length=200)


class WaterFootprint(BaseModel):
    """Estimated agricultural water footprint."""

    model_config = ConfigDict(extra="forbid")

    footprint_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    calculated_at: datetime

    total_water_liters: float = Field(ge=0.0)
    irrigation_water_liters: float = Field(default=0.0, ge=0.0)
    rainfall_contribution_liters: float = Field(default=0.0, ge=0.0)

    water_saved_liters: float = Field(default=0.0, ge=0.0)

    methodology: str = Field(min_length=1, max_length=200)
    methodology_version: str = Field(min_length=1, max_length=100)


__all__ = [
    "WaterFootprint",
    "WaterSource",
    "WaterUseRecord",
]