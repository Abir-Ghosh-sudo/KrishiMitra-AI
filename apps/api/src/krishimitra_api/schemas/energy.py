"""Energy API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EnergyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pump_power_kw: float = Field(..., ge=0)
    flow_rate_lps: float | None = None
    hours: float = Field(..., ge=0)
    motor_efficiency: float | None = None


class EnergyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    energy_kwh: float
    cost_inr: float | None = None
    efficiency: float | None = None
    timestamp: datetime
