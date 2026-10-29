"""Documents API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException

from krishimitra_api.schemas.documents import DocumentUploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{document_id}")
async def get_document(document_id: str) -> dict:
    raise HTTPException(status_code=501, detail="Not implemented")
