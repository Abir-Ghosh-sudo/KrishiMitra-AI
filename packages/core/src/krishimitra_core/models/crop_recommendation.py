"""Crop recommendation models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CropRecommendationStatus(StrEnum):
    """Status of a crop recommendation."""

    GENERATED = "generated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


class CropRecommendation(BaseModel):
    """AI-generated crop recommendation for a farm."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: UUID
    farm_id: UUID

    crop_name: str = Field(min_length=1, max_length=200)
    variety: str | None = Field(default=None, max_length=200)

    suitability_score: float = Field(ge=0.0, le=1.0)
    expected_yield: float | None = Field(default=None, ge=0.0)
    expected_profit_inr: float | None = Field(default=None)

    water_requirement_liters: float | None = Field(
        default=None,
        ge=0.0,
    )

    expected_duration_days: int | None = Field(
        default=None,
        gt=0,
    )

    status: CropRecommendationStatus = CropRecommendationStatus.GENERATED

    reasons: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)


__all__ = [
    "CropRecommendation",
    "CropRecommendationStatus",
]