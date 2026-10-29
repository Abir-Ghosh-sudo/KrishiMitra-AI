"""Predictions API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: str
    crop_id: str | None = None
    features: dict[str, Any] = Field(default_factory=dict)


class PredictionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    predicted_yield: float | None = None
    confidence: float | None = None
    factors: dict[str, float] = Field(default_factory=dict)
    recommendations: list[str] = []
    timestamp: datetime
