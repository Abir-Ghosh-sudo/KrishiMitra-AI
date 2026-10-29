"""Disease API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.disease import DiseasePredictRequest, DiseaseResponse

router = APIRouter(prefix="/disease", tags=["disease"])


@router.post("/predict", response_model=DiseaseResponse)
async def predict_disease(request: DiseasePredictRequest) -> DiseaseResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/history/{farm_id}")
async def get_disease_history(farm_id: str) -> dict:
    return {"farm_id": farm_id, "history": []}
