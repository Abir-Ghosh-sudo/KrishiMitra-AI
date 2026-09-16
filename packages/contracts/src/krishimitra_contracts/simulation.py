"""Simulation service contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SimulationType(StrEnum):
    """Types of what-if simulations supported by KrishiMitra."""

    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    CROP = "crop"
    YIELD = "yield"
    WATER = "water"
    ENERGY = "energy"
    SUSTAINABILITY = "sustainability"
    FARM = "farm"


class SimulationStatus(StrEnum):
    """Lifecycle status of a simulation."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationContract(BaseModel):
    """Completed simulation result exchanged between services."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    simulation_id: UUID

    farmer_id: UUID
    farm_id: UUID | None = None

    simulation_type: SimulationType

    status: SimulationStatus = SimulationStatus.COMPLETED

    inputs: dict[str, Any] = Field(
        default_factory=dict,
    )

    outputs: dict[str, Any] = Field(
        default_factory=dict,
    )

    baseline: dict[str, Any] = Field(
        default_factory=dict,
    )

    comparison: dict[str, Any] = Field(
        default_factory=dict,
    )

    assumptions: tuple[str, ...] = ()

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    model_version: str = Field(
        min_length=1,
        max_length=100,
    )

    explanation: str | None = Field(
        default=None,
        max_length=4000,
    )

    created_at: datetime

    completed_at: datetime | None = None


class SimulationCreateContract(BaseModel):
    """Contract for requesting a what-if farm simulation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    farmer_id: UUID

    farm_id: UUID | None = None

    simulation_type: SimulationType

    inputs: dict[str, Any] = Field(
        default_factory=dict,
    )

    requested_at: datetime


__all__ = [
    "SimulationContract",
    "SimulationCreateContract",
    "SimulationStatus",
    "SimulationType",
]