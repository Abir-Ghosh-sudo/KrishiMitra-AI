"""Documents API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    document_id: str
    filename: str
    status: str
    uploaded_at: datetime
