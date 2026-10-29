"""Feedback API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    category: str | None = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    rating: int
    comment: str | None = None
    category: str | None = None
    created_at: datetime
