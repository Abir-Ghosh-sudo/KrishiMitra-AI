"""Health check models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class HealthStatus(StrEnum):
    """Health state of an application component."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth(BaseModel):
    """Health information for an individual system component."""

    model_config = ConfigDict(extra="forbid")

    component: str = Field(min_length=1, max_length=100)

    status: HealthStatus

    checked_at: datetime

    latency_ms: float | None = Field(default=None, ge=0)

    message: str | None = Field(default=None, max_length=500)


class HealthCheckResponse(BaseModel):
    """Aggregated health status for a KrishiMitra service."""

    model_config = ConfigDict(extra="forbid")

    status: HealthStatus

    service: str = Field(min_length=1, max_length=100)

    version: str = Field(min_length=1, max_length=50)

    checked_at: datetime

    components: list[ComponentHealth] = Field(default_factory=list)


__all__ = [
    "ComponentHealth",
    "HealthCheckResponse",
    "HealthStatus",
]