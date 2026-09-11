"""Geospatial location models for KrishiMitra-AI."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Coordinates(BaseModel):
    """Geographic coordinates using WGS84."""

    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class Location(BaseModel):
    """Farmer or farm location information."""

    model_config = ConfigDict(extra="forbid")

    coordinates: Coordinates
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    state: str | None = None
    district: str | None = None
    village: str | None = None
    postal_code: str | None = None

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str | None) -> str | None:
        """Normalize country codes to uppercase."""
        return value.upper() if value else value


__all__ = [
    "Coordinates",
    "Location",
]