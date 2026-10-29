"""Crop API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CropBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    crop_name: str = Field(..., min_length=1, max_length=100)
    variety: str | None = None
    sowing_date: datetime | None = None
    area_acres: float | None = Field(default=None, ge=0)


class CropCreate(CropBase):
    farm_id: str


class CropUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    crop_name: str | None = Field(default=None, min_length=1, max_length=100)
    variety: str | None = None
    sowing_date: datetime | None = None
    area_acres: float | None = Field(default=None, ge=0)
    status: str | None = None


class CropResponse(CropBase):
    model_config = ConfigDict(extra="ignore")

    id: str
    farm_id: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None
