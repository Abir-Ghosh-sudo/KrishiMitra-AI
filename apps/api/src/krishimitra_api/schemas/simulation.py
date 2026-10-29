"""Simulation API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class SimulationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    results: dict[str, Any]
    recommendations: list[str] = []
    timestamp: datetime
