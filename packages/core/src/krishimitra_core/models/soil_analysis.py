"""Soil analysis and recommendation models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SoilAnalysisSource(StrEnum):
    """Source of soil analysis data."""

    LAB_REPORT = "lab_report"
    IMAGE = "image"
    USER_INPUT = "user_input"
    FIELD_RECORD = "field_record"


class SoilHealthLevel(StrEnum):
    """Overall soil health classification."""

    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"
    UNKNOWN = "unknown"


class SoilAnalysis(BaseModel):
    """Normalized soil analysis extracted from a report or field data."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: UUID
    farm_id: UUID

    source: SoilAnalysisSource

    health_level: SoilHealthLevel = SoilHealthLevel.UNKNOWN

    ph: float | None = Field(default=None, ge=0.0, le=14.0)

    nitrogen_mg_kg: float | None = Field(default=None, ge=0.0)
    phosphorus_mg_kg: float | None = Field(default=None, ge=0.0)
    potassium_mg_kg: float | None = Field(default=None, ge=0.0)

    organic_carbon_percent: float | None = Field(
        default=None,
        ge=0.0,
    )

    electrical_conductivity_ds_m: float | None = Field(
        default=None,
        ge=0.0,
    )

    moisture_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    observations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)


class SoilImprovementRecommendation(BaseModel):
    """Recommendation for improving soil health."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: UUID
    farm_id: UUID

    title: str = Field(min_length=1, max_length=200)
    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    priority: int = Field(default=1, ge=1, le=5)

    expected_benefits: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)

    safety_note: str | None = None


__all__ = [
    "SoilAnalysis",
    "SoilAnalysisSource",
    "SoilHealthLevel",
    "SoilImprovementRecommendation",
]