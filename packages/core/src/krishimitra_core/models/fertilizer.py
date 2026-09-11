"""Fertilizer recommendation models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FertilizerType(StrEnum):
    """Common fertilizer categories."""

    ORGANIC = "organic"
    BIOLOGICAL = "biological"
    MINERAL = "mineral"
    FOLIAR = "foliar"
    SOIL_AMENDMENT = "soil_amendment"


class FertilizerRecommendationStatus(StrEnum):
    """Status of a fertilizer recommendation."""

    GENERATED = "generated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


class NutrientRequirement(BaseModel):
    """Estimated crop nutrient requirement."""

    model_config = ConfigDict(extra="forbid")

    nitrogen_kg_ha: float = Field(default=0.0, ge=0.0)
    phosphorus_kg_ha: float = Field(default=0.0, ge=0.0)
    potassium_kg_ha: float = Field(default=0.0, ge=0.0)


class FertilizerRecommendation(BaseModel):
    """Safe, soil-aware fertilizer recommendation."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    fertilizer_name: str = Field(min_length=1, max_length=200)
    fertilizer_type: FertilizerType

    recommended_quantity_kg: float = Field(gt=0.0)

    nutrient_requirement: NutrientRequirement

    application_method: str = Field(min_length=1, max_length=200)
    application_timing: str = Field(min_length=1, max_length=200)

    status: FertilizerRecommendationStatus = (
        FertilizerRecommendationStatus.GENERATED
    )

    reason: str = Field(min_length=1)
    safety_note: str | None = None

    confidence: float = Field(ge=0.0, le=1.0)

    evidence: list[str] = Field(default_factory=list)


__all__ = [
    "FertilizerRecommendation",
    "FertilizerRecommendationStatus",
    "FertilizerType",
    "NutrientRequirement",
]