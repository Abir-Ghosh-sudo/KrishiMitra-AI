"""Health-check models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from .common import BaseModelSchema


class HealthStatus(StrEnum):
    """Health status values exposed by application services."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModelSchema):
    """Application health-check response."""

    status: HealthStatus
    service: str
    version: str
    timestamp: datetime


class DependencyHealth(BaseModelSchema):
    """Health information for an external dependency."""

    name: str
    status: HealthStatus
    latency_ms: float | None = Field(default=None, ge=0)
    message: str | None = None


class ReadinessResponse(BaseModelSchema):
    """Application readiness response."""

    status: HealthStatus
    service: str
    version: str
    timestamp: datetime
    dependencies: list[DependencyHealth] = Field(default_factory=list)


__all__ = [
    "DependencyHealth",
    "HealthResponse",
    "HealthStatus",
    "ReadinessResponse",
]