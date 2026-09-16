"""Standard service response contracts for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class ResponseStatus(StrEnum):
    """Status of a service response."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


class ContractError(BaseModel):
    """Structured error information returned by a service."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    code: str = Field(
        min_length=1,
        max_length=100,
    )

    message: str = Field(
        min_length=1,
        max_length=1000,
    )

    details: dict[str, str] = Field(default_factory=dict)


class ServiceResponse(BaseModel, Generic[T]):
    """Generic response envelope shared between services."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    status: ResponseStatus

    data: T | None = None

    errors: tuple[ContractError, ...] = ()

    request_id: str | None = Field(
        default=None,
        max_length=128,
    )

    service: str = Field(
        min_length=1,
        max_length=100,
    )


__all__ = [
    "ContractError",
    "ResponseStatus",
    "ServiceResponse",
]