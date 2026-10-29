"""Sustainability API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SustainabilityResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    score: float
    carbon_footprint_kg: float | None = None
    water_usage_liters: float | None = None
    recommendations: list[str] = []
    timestamp: datetime
