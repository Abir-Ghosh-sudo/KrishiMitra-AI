"""Predictions API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.predictions import PredictionRequest, PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/yield", response_model=PredictionResponse)
async def predict_yield(request: PredictionRequest) -> PredictionResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/history/{farm_id}")
async def get_prediction_history(farm_id: str) -> dict:
    return {"farm_id": farm_id, "history": []}
