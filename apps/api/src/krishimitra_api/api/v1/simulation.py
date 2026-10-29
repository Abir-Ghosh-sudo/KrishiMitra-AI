"""Simulation API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.simulation import SimulationRequest, SimulationResponse

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest) -> SimulationResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/scenarios")
async def get_scenarios() -> dict:
    return {"scenarios": []}
