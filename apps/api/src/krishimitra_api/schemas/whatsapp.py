"""WhatsApp API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WhatsAppWebhook(BaseModel):
    model_config = ConfigDict(extra="allow")

    object: str | None = None
    entry: list[dict] = Field(default_factory=list)


class WhatsAppResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
