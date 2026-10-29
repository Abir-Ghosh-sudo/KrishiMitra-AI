"""Disease API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DiseasePredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_data: str = Field(..., description="Base64 encoded image")
    crop_type: str | None = None
    farm_id: str | None = None


class DiseasePrediction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    disease: str
    confidence: float
    probabilities: dict[str, float]
    treatment_advice: str | None = None
    severity: str | None = None


class DiseaseResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prediction: DiseasePrediction
    status: str
    request_id: str | None = None
    timestamp: datetime | None = None
