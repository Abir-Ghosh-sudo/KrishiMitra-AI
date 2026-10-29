"""Irrigation API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IrrigationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: str
    crop_id: str | None = None
    soil_moisture: float | None = None
    temperature: float | None = None
    humidity: float | None = None


class IrrigationRecommendation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    should_irrigate: bool
    water_amount_mm: float
    duration_minutes: float | None = None
    reason: str | None = None
    confidence: float | None = None


class IrrigationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    recommendation: IrrigationRecommendation
    timestamp: datetime
