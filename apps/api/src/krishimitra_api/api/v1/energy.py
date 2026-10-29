"""Energy API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.energy import EnergyRequest, EnergyResponse

router = APIRouter(prefix="/energy", tags=["energy"])


@router.post("/calculate", response_model=EnergyResponse)
async def calculate_energy(request: EnergyRequest) -> EnergyResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/usage/{farm_id}")
async def get_energy_usage(farm_id: str) -> dict:
    return {"farm_id": farm_id, "usage": []}
