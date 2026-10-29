"""Sustainability API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.sustainability import SustainabilityResponse

router = APIRouter(prefix="/sustainability", tags=["sustainability"])


@router.get("/score/{farm_id}", response_model=SustainabilityResponse)
async def get_sustainability_score(farm_id: str) -> SustainabilityResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/carbon/{farm_id}")
async def get_carbon_footprint(farm_id: str) -> dict:
    return {"farm_id": farm_id, "carbon_footprint_kg": 0.0}
