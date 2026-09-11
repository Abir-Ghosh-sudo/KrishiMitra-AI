"""Cursor pagination models for KrishiMitra-AI."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


CursorT = TypeVar("CursorT")


class CursorPage(BaseModel, Generic[CursorT]):
    """Generic cursor-paginated response."""

    model_config = ConfigDict(extra="forbid")

    items: list[CursorT] = Field(default_factory=list)

    next_cursor: str | None = None
    previous_cursor: str | None = None

    has_next: bool = False
    has_previous: bool = False

    page_size: int = Field(default=20, ge=1, le=100)


class CursorRequest(BaseModel):
    """Request parameters for cursor-based pagination."""

    model_config = ConfigDict(extra="forbid")

    cursor: str | None = None

    limit: int = Field(default=20, ge=1, le=100)

    direction: str = Field(
        default="forward",
        pattern="^(forward|backward)$",
    )


__all__ = [
    "CursorPage",
    "CursorRequest",
]