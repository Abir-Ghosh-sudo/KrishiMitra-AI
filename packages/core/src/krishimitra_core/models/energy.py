"""Energy optimization models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EnergySource(StrEnum):
    """Energy sources used by farm operations."""

    GRID = "grid"
    SOLAR = "solar"
    DIESEL = "diesel"
    BATTERY = "battery"
    OTHER = "other"


class EnergyOptimizationStatus(StrEnum):
    """Status of an energy optimization recommendation."""

    GENERATED = "generated"
    ACCEPTED = "accepted"
    APPLIED = "applied"
    REJECTED = "rejected"
    EXPIRED = "expired"


class EnergyObservation(BaseModel):
    """Observed energy usage for a farm operation."""

    model_config = ConfigDict(extra="forbid")

    observation_id: UUID
    farm_id: UUID

    observed_at: datetime

    source: EnergySource
    energy_kwh: float = Field(ge=0.0)

    operation: str = Field(min_length=1, max_length=200)

    cost_inr: float | None = Field(default=None, ge=0.0)


class EnergyOptimization(BaseModel):
    """AI/optimization-generated energy saving recommendation."""

    model_config = ConfigDict(extra="forbid")

    optimization_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    created_at: datetime

    status: EnergyOptimizationStatus = EnergyOptimizationStatus.GENERATED

    current_energy_kwh: float = Field(ge=0.0)
    optimized_energy_kwh: float = Field(ge=0.0)

    energy_saved_kwh: float = Field(ge=0.0)
    estimated_cost_saved_inr: float = Field(default=0.0, ge=0.0)

    recommended_source: EnergySource | None = None

    recommendation: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    confidence: float = Field(ge=0.0, le=1.0)

    @property
    def savings_percent(self) -> float:
        """Return estimated percentage energy savings."""
        if self.current_energy_kwh == 0:
            return 0.0

        return (
            self.energy_saved_kwh
            / self.current_energy_kwh
        ) * 100


__all__ = [
    "EnergyObservation",
    "EnergyOptimization",
    "EnergyOptimizationStatus",
    "EnergySource",
]