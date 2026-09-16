"""Base contract primitives for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseContract(BaseModel):
    """Base model shared by inter-service request and response contracts."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    contract_id: UUID

    contract_version: str = Field(
        default="1.0",
        min_length=1,
        max_length=20,
    )

    created_at: datetime

    request_id: UUID | None = None

    metadata: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "BaseContract",
]