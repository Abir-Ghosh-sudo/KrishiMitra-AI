"""Farm what-if simulation models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SimulationType(StrEnum):
    """Supported farm simulation scenarios."""

    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    CROP = "crop"
    WEATHER = "weather"
    PEST = "pest"
    DISEASE = "disease"
    ENERGY = "energy"
    SUSTAINABILITY = "sustainability"
    COMBINED = "combined"


class SimulationStatus(StrEnum):
    """Lifecycle status of a simulation."""

    REQUESTED = "requested"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationInput(BaseModel):
    """Input parameter for a farm what-if simulation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    value: float | str | bool
    unit: str | None = Field(default=None, max_length=50)


class SimulationMetric(BaseModel):
    """Metric produced by a simulation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    baseline_value: float
    simulated_value: float
    unit: str | None = Field(default=None, max_length=50)

    @property
    def change(self) -> float:
        """Return the absolute change from baseline."""
        return self.simulated_value - self.baseline_value


class FarmSimulation(BaseModel):
    """Result of a farm what-if simulation."""

    model_config = ConfigDict(extra="forbid")

    simulation_id: UUID
    farm_id: UUID
    crop_id: UUID | None = None

    simulation_type: SimulationType
    status: SimulationStatus = SimulationStatus.REQUESTED

    scenario_name: str = Field(min_length=1, max_length=200)

    inputs: list[SimulationInput] = Field(default_factory=list)
    metrics: list[SimulationMetric] = Field(default_factory=list)

    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)

    model_version: str = Field(min_length=1, max_length=100)


__all__ = [
    "FarmSimulation",
    "SimulationInput",
    "SimulationMetric",
    "SimulationStatus",
    "SimulationType",
]