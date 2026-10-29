"""Irrigation API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.irrigation import IrrigationRequest, IrrigationResponse

router = APIRouter(prefix="/irrigation", tags=["irrigation"])


@router.post("/recommend", response_model=IrrigationResponse)
async def recommend_irrigation(request: IrrigationRequest) -> IrrigationResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/schedule/{farm_id}")
async def get_irrigation_schedule(farm_id: str) -> dict:
    return {"farm_id": farm_id, "schedule": []}
