"""Carbon and climate impact models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CarbonFootprint(BaseModel):
    """Estimated greenhouse-gas footprint of farm activities."""

    model_config = ConfigDict(extra="forbid")

    footprint_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    calculated_at: datetime

    total_kg_co2e: float = Field(ge=0.0)

    energy_kg_co2e: float = Field(default=0.0, ge=0.0)
    fertilizer_kg_co2e: float = Field(default=0.0, ge=0.0)
    irrigation_kg_co2e: float = Field(default=0.0, ge=0.0)
    transport_kg_co2e: float = Field(default=0.0, ge=0.0)
    other_kg_co2e: float = Field(default=0.0, ge=0.0)

    methodology: str = Field(min_length=1, max_length=200)
    methodology_version: str = Field(min_length=1, max_length=100)


class CarbonReductionRecommendation(BaseModel):
    """Recommendation for reducing farm greenhouse-gas emissions."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: UUID
    farm_id: UUID

    created_at: datetime

    title: str = Field(min_length=1, max_length=200)
    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    estimated_reduction_kg_co2e: float = Field(ge=0.0)

    confidence: float = Field(ge=0.0, le=1.0)

    evidence: list[str] = Field(default_factory=list)


__all__ = [
    "CarbonFootprint",
    "CarbonReductionRecommendation",
]