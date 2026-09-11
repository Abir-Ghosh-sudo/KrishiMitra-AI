"""Pagination models for KrishiMitra-AI."""

from __future__ import annotations

from pydantic import Field

from .common import BaseModelSchema


class PaginationParams(BaseModelSchema):
    """Validated pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Return the database offset for the current page."""
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseModelSchema):
    """Pagination metadata returned to API clients."""

    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(default=0, ge=0)

    @property
    def total_pages(self) -> int:
        """Return the total number of available pages."""
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


__all__ = [
    "PaginationMeta",
    "PaginationParams",
]