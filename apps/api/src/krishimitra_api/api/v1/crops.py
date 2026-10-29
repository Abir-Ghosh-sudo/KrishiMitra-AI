"""Crops API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from krishimitra_api.schemas.crop import CropCreate, CropUpdate, CropResponse

router = APIRouter(prefix="/crops", tags=["crops"])


@router.get("", response_model=list[CropResponse])
async def list_crops(farm_id: str | None = None, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100)) -> list[CropResponse]:
    return []


@router.post("", response_model=CropResponse)
async def create_crop(crop: CropCreate) -> CropResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(crop_id: str) -> CropResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{crop_id}", response_model=CropResponse)
async def update_crop(crop_id: str, crop: CropUpdate) -> CropResponse:
    raise HTTPException(status_code=501, detail="Not implemented")
