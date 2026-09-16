"""Prediction service contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PredictionType(StrEnum):
    """Types of predictions produced by KrishiMitra AI/ML services."""

    YIELD = "yield"
    DISEASE_RISK = "disease_risk"
    PEST_RISK = "pest_risk"
    IRRIGATION = "irrigation"
    CROP = "crop"
    FERTILIZER = "fertilizer"
    WEATHER_IMPACT = "weather_impact"


class PredictionStatus(StrEnum):
    """Lifecycle status of a prediction."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class PredictionContract(BaseModel):
    """Shared prediction result exchanged between services."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    prediction_id: UUID

    farmer_id: UUID
    farm_id: UUID | None = None
    crop_id: UUID | None = None

    prediction_type: PredictionType

    status: PredictionStatus = PredictionStatus.COMPLETED

    value: float | None = None

    unit: str | None = Field(
        default=None,
        max_length=50,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    model_name: str = Field(
        min_length=1,
        max_length=200,
    )

    model_version: str = Field(
        min_length=1,
        max_length=100,
    )

    prediction_window_start: datetime | None = None
    prediction_window_end: datetime | None = None

    features: dict[str, Any] = Field(
        default_factory=dict,
    )

    explanation: str | None = Field(
        default=None,
        max_length=4000,
    )

    created_at: datetime

    expires_at: datetime | None = None


class PredictionCreateContract(BaseModel):
    """Contract for creating a prediction request."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    farmer_id: UUID

    farm_id: UUID | None = None
    crop_id: UUID | None = None

    prediction_type: PredictionType

    features: dict[str, Any] = Field(
        default_factory=dict,
    )

    requested_at: datetime


__all__ = [
    "PredictionContract",
    "PredictionCreateContract",
    "PredictionStatus",
    "PredictionType",
]