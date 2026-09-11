"""Soil models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SoilTexture(StrEnum):
    """Common soil texture classes."""

    SANDY = "sandy"
    LOAMY = "loamy"
    CLAY = "clay"
    SILTY = "silty"
    SANDY_LOAM = "sandy_loam"
    CLAY_LOAM = "clay_loam"
    SILT_LOAM = "silt_loam"
    UNKNOWN = "unknown"


class SoilProfile(BaseModel):
    """Normalized soil information for a farm."""

    model_config = ConfigDict(extra="forbid")

    soil_id: UUID
    farm_id: UUID

    texture: SoilTexture = SoilTexture.UNKNOWN

    ph: float | None = Field(default=None, ge=0.0, le=14.0)

    nitrogen_mg_kg: float | None = Field(default=None, ge=0.0)
    phosphorus_mg_kg: float | None = Field(default=None, ge=0.0)
    potassium_mg_kg: float | None = Field(default=None, ge=0.0)

    organic_carbon_percent: float | None = Field(default=None, ge=0.0)
    electrical_conductivity_ds_m: float | None = Field(default=None, ge=0.0)

    moisture_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )


__all__ = [
    "SoilProfile",
    "SoilTexture",
]