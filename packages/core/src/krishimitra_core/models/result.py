"""Generic result models for KrishiMitra-AI."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import Field

from .common import BaseModelSchema


T = TypeVar("T")


class Result(BaseModelSchema, Generic[T]):
    """Represent a successful or failed operation."""

    success: bool
    data: T | None = None
    error_code: str | None = None
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(
        cls,
        data: T | None = None,
        *,
        message: str | None = None,
    ) -> "Result[T]":
        """Create a successful result."""
        return cls(
            success=True,
            data=data,
            message=message,
        )

    @classmethod
    def failure(
        cls,
        error_code: str,
        *,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> "Result[T]":
        """Create a failed result."""
        return cls(
            success=False,
            error_code=error_code,
            message=message,
            details=details or {},
        )


__all__ = [
    "Result",
]