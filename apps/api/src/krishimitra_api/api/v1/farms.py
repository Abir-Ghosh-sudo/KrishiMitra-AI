"""Farms API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any

from krishimitra_api.schemas.farm import FarmCreate, FarmUpdate, FarmResponse, FarmListResponse

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get("", response_model=FarmListResponse)
async def list_farms(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100)) -> FarmListResponse:
    """List all farms."""
    return FarmListResponse(farms=[], total=0)


@router.post("", response_model=FarmResponse)
async def create_farm(farm: FarmCreate) -> FarmResponse:
    """Create a new farm."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: str) -> FarmResponse:
    """Get farm by ID."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(farm_id: str, farm: FarmUpdate) -> FarmResponse:
    """Update farm."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{farm_id}")
async def delete_farm(farm_id: str) -> dict:
    """Delete farm."""
    raise HTTPException(status_code=501, detail="Not implemented")
