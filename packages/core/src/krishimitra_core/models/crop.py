"""Crop models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CropStage(StrEnum):
    """Common crop growth stages."""

    SEEDING = "seeding"
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURATION = "maturation"
    HARVEST = "harvest"
    POST_HARVEST = "post_harvest"


class Crop(BaseModel):
    """Crop currently associated with a farm."""

    model_config = ConfigDict(extra="forbid")

    crop_id: UUID
    farm_id: UUID

    name: str = Field(min_length=1, max_length=200)
    variety: str | None = None

    area_hectares: float = Field(gt=0)

    stage: CropStage
    planting_date: date

    expected_harvest_date: date | None = None

    irrigation_required: bool = True


__all__ = [
    "Crop",
    "CropStage",
]