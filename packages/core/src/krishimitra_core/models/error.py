"""Error response models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from .common import BaseModelSchema


class ErrorDetail(BaseModelSchema):
    """Structured application error details."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModelSchema):
    """Standard API error response."""

    error: ErrorDetail
    request_id: str | None = None
    timestamp: datetime


__all__ = [
    "ErrorDetail",
    "ErrorResponse",
]