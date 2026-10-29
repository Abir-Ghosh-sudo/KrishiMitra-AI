"""Pest API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PestRiskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: str
    crop_id: str | None = None
    temperature: float | None = None
    humidity: float | None = None


class PestRiskResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    risk_level: str
    risk_score: float
    recommendations: list[str] = []
    timestamp: datetime
