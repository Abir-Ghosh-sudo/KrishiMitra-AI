"""Media models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class MediaType(StrEnum):
    """Supported inbound and outbound media types."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class MediaMetadata(BaseModel):
    """Metadata associated with a media object."""

    model_config = ConfigDict(extra="forbid")

    media_type: MediaType
    mime_type: str = Field(min_length=1)
    file_name: str | None = None
    file_size_bytes: int | None = Field(default=None, ge=0)
    duration_seconds: float | None = Field(default=None, ge=0)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    checksum: str | None = None


class MediaReference(BaseModel):
    """Secure reference to stored media."""

    model_config = ConfigDict(extra="forbid")

    media_id: str = Field(min_length=1)
    metadata: MediaMetadata
    storage_key: str = Field(min_length=1)


__all__ = [
    "MediaMetadata",
    "MediaReference",
    "MediaType",
]