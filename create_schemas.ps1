# Create all schemas
$schemas = @{
"farm.py" = @"
""""Farm API schemas.""""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FarmBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=200)
    area_acres: float | None = Field(default=None, ge=0)
    location: dict[str, Any] | None = None
    soil_type: str | None = None
    irrigation_type: str | None = None


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    area_acres: float | None = Field(default=None, ge=0)
    location: dict[str, Any] | None = None
    soil_type: str | None = None
    irrigation_type: str | None = None


class FarmResponse(FarmBase):
    model_config = ConfigDict(extra="ignore")

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime | None = None


class FarmListResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    farms: list[FarmResponse]
    total: int
"@
}
$base = "C:\Users\ABIR\OneDrive\Desktop\hacathon\KrishiMitra-AI\apps\api\src\krishimitra_api\schemas"
foreach($k in $schemas.Keys){
    Set-Content -Path (Join-Path $base $k) -Value $schemas[$k] -Encoding UTF8
}
Write-Host "done"