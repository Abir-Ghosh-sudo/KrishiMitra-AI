"""Sustainability models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SustainabilityScore(BaseModel):
    """Farm-level sustainability assessment."""

    model_config = ConfigDict(extra="forbid")

    score_id: UUID
    farm_id: UUID

    calculated_at: datetime

    overall_score: float = Field(ge=0.0, le=100.0)

    water_efficiency_score: float = Field(ge=0.0, le=100.0)
    energy_efficiency_score: float = Field(ge=0.0, le=100.0)
    soil_health_score: float = Field(ge=0.0, le=100.0)
    chemical_use_score: float = Field(ge=0.0, le=100.0)
    biodiversity_score: float = Field(ge=0.0, le=100.0)

    carbon_footprint_kg_co2e: float = Field(ge=0.0)
    water_footprint_liters: float = Field(ge=0.0)

    key_strengths: list[str] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)


class SustainabilityRecommendation(BaseModel):
    """Action intended to improve farm sustainability."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: UUID
    farm_id: UUID

    created_at: datetime

    title: str = Field(min_length=1, max_length=200)
    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    estimated_water_saving_liters: float = Field(
        default=0.0,
        ge=0.0,
    )
    estimated_energy_saving_kwh: float = Field(
        default=0.0,
        ge=0.0,
    )
    estimated_carbon_reduction_kg_co2e: float = Field(
        default=0.0,
        ge=0.0,
    )

    priority: int = Field(default=1, ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)


__all__ = [
    "SustainabilityRecommendation",
    "SustainabilityScore",
]