"""Operation lifecycle models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OperationStatus(StrEnum):
    """Lifecycle state of an asynchronous operation."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class OperationType(StrEnum):
    """Supported asynchronous operation categories."""

    WHATSAPP_MESSAGE = "whatsapp_message"
    SPEECH_TRANSCRIPTION = "speech_transcription"
    VISION_ANALYSIS = "vision_analysis"
    DOCUMENT_PROCESSING = "document_processing"
    AI_INFERENCE = "ai_inference"
    RAG_RETRIEVAL = "rag_retrieval"
    WEATHER_REFRESH = "weather_refresh"
    DISEASE_ANALYSIS = "disease_analysis"
    PEST_ANALYSIS = "pest_analysis"
    IRRIGATION_ANALYSIS = "irrigation_analysis"
    NOTIFICATION = "notification"


class Operation(BaseModel):
    """Track execution state of a background operation."""

    model_config = ConfigDict(extra="forbid")

    operation_id: UUID

    operation_type: OperationType

    status: OperationStatus = OperationStatus.QUEUED

    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    retry_count: int = Field(default=0, ge=0)

    worker_id: str | None = Field(default=None, max_length=200)

    result_reference: str | None = Field(default=None, max_length=500)

    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = Field(default=None, max_length=2000)

    metadata: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "Operation",
    "OperationStatus",
    "OperationType",
]