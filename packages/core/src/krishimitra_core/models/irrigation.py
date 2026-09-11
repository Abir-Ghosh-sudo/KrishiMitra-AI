"""Irrigation models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IrrigationMethod(StrEnum):
    """Supported irrigation methods."""

    DRIP = "drip"
    SPRINKLER = "sprinkler"
    FLOOD = "flood"
    FURROW = "furrow"
    BASIN = "basin"
    MANUAL = "manual"
    OTHER = "other"


class IrrigationStatus(StrEnum):
    """Status of an irrigation recommendation or schedule."""

    PLANNED = "planned"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class IrrigationRecommendation(BaseModel):
    """AI-generated irrigation recommendation."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    method: IrrigationMethod

    recommended_at: datetime
    duration_minutes: float = Field(gt=0)
    water_required_liters: float = Field(gt=0)

    soil_moisture_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    rainfall_expected_mm: float | None = Field(
        default=None,
        ge=0.0,
    )

    water_saved_liters: float = Field(default=0.0, ge=0.0)
    energy_saved_kwh: float = Field(default=0.0, ge=0.0)

    confidence: float = Field(ge=0.0, le=1.0)

    reason: str = Field(min_length=1)
    safety_note: str | None = None


class IrrigationSchedule(BaseModel):
    """Scheduled irrigation event for a farm."""

    model_config = ConfigDict(extra="forbid")

    schedule_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    method: IrrigationMethod

    start_time: datetime
    duration_minutes: float = Field(gt=0)

    target_water_liters: float = Field(gt=0)

    status: IrrigationStatus = IrrigationStatus.PLANNED

    weather_adjusted: bool = False
    rainfall_avoided_mm: float | None = Field(
        default=None,
        ge=0.0,
    )

    created_at: datetime


__all__ = [
    "IrrigationMethod",
    "IrrigationRecommendation",
    "IrrigationSchedule",
    "IrrigationStatus",
]