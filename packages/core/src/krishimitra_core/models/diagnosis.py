"""Crop diagnosis models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .confidence import ConfidenceScore


class DiagnosisType(StrEnum):
    """Types of agricultural diagnosis."""

    DISEASE = "disease"
    PEST = "pest"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    PHYSIOLOGICAL = "physiological"
    UNKNOWN = "unknown"


class DiagnosisStatus(StrEnum):
    """Diagnosis processing status."""

    COMPLETED = "completed"
    LOW_CONFIDENCE = "low_confidence"
    REQUIRES_EXPERT = "requires_expert"
    INCONCLUSIVE = "inconclusive"


class DiagnosisEvidence(BaseModel):
    """Evidence supporting an agricultural diagnosis."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1)
    description: str = Field(min_length=1)
    relevance: float = Field(ge=0.0, le=1.0)


class Diagnosis(BaseModel):
    """Normalized AI/ML agricultural diagnosis."""

    model_config = ConfigDict(extra="forbid")

    diagnosis_id: UUID
    farm_id: UUID | None = None
    crop_id: UUID | None = None

    diagnosis_type: DiagnosisType
    status: DiagnosisStatus

    label: str = Field(min_length=1)
    confidence: ConfidenceScore

    evidence: list[DiagnosisEvidence] = Field(default_factory=list)

    requires_expert_review: bool = False
    explanation: str | None = None


__all__ = [
    "Diagnosis",
    "DiagnosisEvidence",
    "DiagnosisStatus",
    "DiagnosisType",
]
