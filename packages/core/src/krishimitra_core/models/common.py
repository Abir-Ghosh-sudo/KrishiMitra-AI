"""Common shared models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class BaseModelSchema(BaseModel):
    """Base Pydantic model with strict shared configuration."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        from_attributes=True,
    )


class TimestampedModel(BaseModelSchema):
    """Base model containing creation and update timestamps."""

    created_at: datetime
    updated_at: datetime


class IdentifierModel(BaseModelSchema):
    """Base model containing a resource identifier."""

    id: UUID


class PaginatedResponse(BaseModelSchema, Generic[T]):
    """Generic paginated API response."""

    items: list[T] = Field(default_factory=list)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)
    total: int = Field(default=0, ge=0)

    @property
    def total_pages(self) -> int:
        """Return the number of available pages."""
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


__all__ = [
    "BaseModelSchema",
    "IdentifierModel",
    "PaginatedResponse",
    "TimestampedModel",
]