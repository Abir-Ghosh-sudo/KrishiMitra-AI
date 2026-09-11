"""Agricultural document models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentType(StrEnum):
    """Supported agricultural document types."""

    SOIL_REPORT = "soil_report"
    CROP_REPORT = "crop_report"
    FARM_RECORD = "farm_record"
    GOVERNMENT_SCHEME = "government_scheme"
    AGRICULTURAL_GUIDE = "agricultural_guide"
    INVOICE = "invoice"
    OTHER = "other"


class DocumentProcessingStatus(StrEnum):
    """Document processing lifecycle."""

    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class Document(BaseModel):
    """Normalized agricultural document metadata."""

    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    farmer_id: UUID
    farm_id: UUID | None = None

    document_type: DocumentType = DocumentType.OTHER
    status: DocumentProcessingStatus = DocumentProcessingStatus.RECEIVED

    file_name: str = Field(min_length=1, max_length=500)
    mime_type: str = Field(min_length=1, max_length=200)
    file_size_bytes: int = Field(ge=0)

    storage_key: str = Field(min_length=1)

    uploaded_at: datetime
    processed_at: datetime | None = None

    extracted_text: str | None = None
    extraction_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    page_count: int | None = Field(default=None, gt=0)

    processing_error: str | None = None


class DocumentChunk(BaseModel):
    """Searchable chunk extracted from an agricultural document."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: UUID
    document_id: UUID

    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)

    page_number: int | None = Field(default=None, gt=0)

    embedding_id: str | None = None

    metadata: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "Document",
    "DocumentChunk",
    "DocumentProcessingStatus",
    "DocumentType",
]