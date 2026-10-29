"""Feedback API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from krishimitra_api.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
async def create_feedback(feedback: FeedbackCreate) -> FeedbackResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("")
async def list_feedback() -> dict:
    return {"feedback": [], "total": 0}
