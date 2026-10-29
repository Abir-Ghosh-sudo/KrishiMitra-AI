"""Pest API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.pest import PestRiskRequest, PestRiskResponse

router = APIRouter(prefix="/pest", tags=["pest"])


@router.post("/risk", response_model=PestRiskResponse)
async def assess_pest_risk(request: PestRiskRequest) -> PestRiskResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/alerts/{farm_id}")
async def get_pest_alerts(farm_id: str) -> dict:
    return {"farm_id": farm_id, "alerts": []}
