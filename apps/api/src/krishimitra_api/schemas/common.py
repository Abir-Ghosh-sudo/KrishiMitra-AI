"""Common API response schemas, envelopes, and pagination models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIStatus(StrEnum):
    """Status strings for unified API responses."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class APIErrorDetail(BaseModel):
    """Structured error detail representation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(..., description="Machine-readable error identifier code")
    message: str = Field(..., description="Human-readable error description")
    location: str | None = Field(
        default=None,
        description="Location of error, e.g. field path or parameter name",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context or diagnostics for the error",
    )


class APIResponse(BaseModel, Generic[T]):
    """Standard unified response envelope for all REST endpoints."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    status: APIStatus = Field(
        default=APIStatus.SUCCESS,
        description="Overall status of the operation",
    )
    data: T | None = Field(
        default=None,
        description="Response payload data when successful",
    )
    errors: list[APIErrorDetail] = Field(
        default_factory=list,
        description="List of errors if the operation failed or had partial errors",
    )
    message: str | None = Field(
        default=None,
        description="Optional human-readable informational message",
    )
    request_id: str | None = Field(
        default=None,
        description="Unique request tracing ID",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of response generation",
    )


class PaginationParams(BaseModel):
    """Common query parameters for paginated endpoints."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1, description="1-indexed page number")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (maximum 100)",
    )

    @property
    def offset(self) -> int:
        """Calculate database row offset."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Alias for page_size for ORM query mapping."""
        return self.page_size


class PageMetadata(BaseModel):
    """Metadata describing pagination state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Requested page size")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total calculated pages")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_prev: bool = Field(..., description="Whether a previous page exists")

    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> PageMetadata:
        """Factory constructor computing pages and navigation flags."""
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1 and total_pages > 0,
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard response model for paginated list endpoints."""

    model_config = ConfigDict(extra="forbid")

    items: list[T] = Field(default_factory=list, description="List of items for current page")
    pagination: PageMetadata = Field(..., description="Pagination metadata")


class HealthStatus(StrEnum):
    """System health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health check status for an individual subsystem or dependency."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Component identifier, e.g. postgres, redis, celery")
    status: HealthStatus = Field(..., description="Component health status")
    latency_ms: float | None = Field(default=None, description="Check round-trip latency in ms")
    details: dict[str, Any] = Field(default_factory=dict, description="Diagnostic attributes")


class HealthCheckResponse(BaseModel):
    """System-wide health check report."""

    model_config = ConfigDict(extra="forbid")

    status: HealthStatus = Field(..., description="Overall system health")
    version: str = Field(default="0.1.0", description="API version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of health evaluation",
    )
    components: list[ComponentHealth] = Field(
        default_factory=list,
        description="Health details for subsystems",
    )


__all__ = [
    "APIErrorDetail",
    "APIResponse",
    "APIStatus",
    "ComponentHealth",
    "HealthCheckResponse",
    "HealthStatus",
    "PageMetadata",
    "PaginatedResponse",
    "PaginationParams",
]
