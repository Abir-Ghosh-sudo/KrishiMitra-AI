"""Crop yield prediction models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class YieldUnit(StrEnum):
    """Common agricultural yield units."""

    KG = "kg"
    QUINTAL = "quintal"
    TONNE = "tonne"


class YieldPredictionStatus(StrEnum):
    """Status of a yield prediction."""

    GENERATED = "generated"
    UPDATED = "updated"
    LOW_CONFIDENCE = "low_confidence"
    REQUIRES_REVIEW = "requires_review"


class YieldPrediction(BaseModel):
    """AI/ML crop yield prediction with uncertainty."""

    model_config = ConfigDict(extra="forbid")

    prediction_id: UUID
    farm_id: UUID
    crop_id: UUID

    predicted_at: datetime

    predicted_yield: float = Field(ge=0.0)
    lower_bound: float = Field(ge=0.0)
    upper_bound: float = Field(ge=0.0)

    unit: YieldUnit = YieldUnit.KG

    confidence: float = Field(ge=0.0, le=1.0)

    model_name: str = Field(min_length=1, max_length=200)
    model_version: str = Field(min_length=1, max_length=100)

    status: YieldPredictionStatus = YieldPredictionStatus.GENERATED

    contributing_factors: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @property
    def prediction_range(self) -> float:
        """Return the width of the predicted yield range."""
        return self.upper_bound - self.lower_bound


__all__ = [
    "YieldPrediction",
    "YieldPredictionStatus",
    "YieldUnit",
]