"""WhatsApp API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from krishimitra_api.schemas.whatsapp import WhatsAppWebhook, WhatsAppResponse

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
async def verify_webhook(request: Request) -> dict:
    return {"status": "ok"}


@router.post("/webhook", response_model=WhatsAppResponse)
async def webhook(request: Request) -> WhatsAppResponse:
    return WhatsAppResponse(status="ok")
