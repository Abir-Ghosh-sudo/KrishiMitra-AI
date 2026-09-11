"""Pest detection and risk models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .confidence import ConfidenceScore


class PestRiskLevel(StrEnum):
    """Pest risk levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PestDiagnosisStatus(StrEnum):
    """Status of pest diagnosis."""

    COMPLETED = "completed"
    LOW_CONFIDENCE = "low_confidence"
    REQUIRES_EXPERT = "requires_expert"
    INCONCLUSIVE = "inconclusive"


class PestEvidence(BaseModel):
    """Evidence supporting a pest identification."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1)
    description: str = Field(min_length=1)
    relevance: float = Field(ge=0.0, le=1.0)


class PestDiagnosis(BaseModel):
    """AI/ML pest identification result."""

    model_config = ConfigDict(extra="forbid")

    diagnosis_id: UUID
    farm_id: UUID | None = None
    crop_id: UUID | None = None

    pest_name: str = Field(min_length=1, max_length=200)
    status: PestDiagnosisStatus

    confidence: ConfidenceScore

    evidence: list[PestEvidence] = Field(default_factory=list)

    affected_area_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    requires_expert_review: bool = False
    explanation: str | None = None


class PestRiskPrediction(BaseModel):
    """Predicted future pest risk for a farm or crop."""

    model_config = ConfigDict(extra="forbid")

    prediction_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    pest_name: str = Field(min_length=1, max_length=200)

    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: PestRiskLevel

    contributing_factors: list[str] = Field(default_factory=list)

    recommended_monitoring: list[str] = Field(default_factory=list)

    model_name: str = Field(min_length=1, max_length=200)
    model_version: str = Field(min_length=1, max_length=100)


__all__ = [
    "PestDiagnosis",
    "PestDiagnosisStatus",
    "PestEvidence",
    "PestRiskLevel",
    "PestRiskPrediction",
]