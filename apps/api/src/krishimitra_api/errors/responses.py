"""Error response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    location: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class APIErrorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str = "error"
    message: str
    errors: list[APIErrorDetail] = Field(default_factory=list)


def error_response(message: str, errors: list[APIErrorDetail] | None = None) -> dict[str, Any]:
    return {"status": "error", "message": message, "errors": errors or []}
