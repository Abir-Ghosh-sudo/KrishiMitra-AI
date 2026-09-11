"""Disease risk prediction models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DiseaseRiskLevel(StrEnum):
    """Disease risk levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DiseaseRiskPrediction(BaseModel):
    """Predicted disease risk based on crop, weather, and farm context."""

    model_config = ConfigDict(extra="forbid")

    prediction_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    disease_name: str = Field(min_length=1, max_length=200)

    predicted_at: datetime
    valid_until: datetime | None = None

    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: DiseaseRiskLevel

    contributing_factors: list[str] = Field(default_factory=list)

    weather_signals: list[str] = Field(default_factory=list)
    crop_signals: list[str] = Field(default_factory=list)

    recommended_actions: list[str] = Field(default_factory=list)

    model_name: str = Field(min_length=1, max_length=200)
    model_version: str = Field(min_length=1, max_length=100)

    confidence: float = Field(ge=0.0, le=1.0)


__all__ = [
    "DiseaseRiskLevel",
    "DiseaseRiskPrediction",
]