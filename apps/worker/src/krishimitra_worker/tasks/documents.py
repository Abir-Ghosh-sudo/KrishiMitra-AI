from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from celery import Task

from krishimitra_worker.celery_app import celery_app

logger = logging.getLogger(__name__)


class DocumentTaskError(RuntimeError):
    """Raised when document processing fails."""


class DocumentProcessingTask(Task):
    """
    Base Celery task for agricultural document workloads.

    OCR, document parsing, extraction, chunking, and embedding are
    intentionally kept outside the Celery task boundary.
    """

    autoretry_for = (DocumentTaskError,)
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    max_retries = 5


@celery_app.task(
    bind=True,
    base=DocumentProcessingTask,
    name="krishimitra_worker.tasks.documents.process_document",
)
def process_document(
    self: DocumentProcessingTask,
    *,
    message_id: str,
    document_id: str,
    request_id: str | None = None,
    document_type: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Process an agricultural document asynchronously.

    The task receives a persisted document reference rather than
    transferring the complete file through the Celery broker.

    Supported future document workloads include:

    - Soil reports
    - Agricultural PDFs
    - Lab reports
    - Fertilizer reports
    - Crop documents
    - Government/agricultural advisory documents
    """

    if not message_id.strip():
        raise DocumentTaskError("message_id cannot be empty.")

    if not document_id.strip():
        raise DocumentTaskError("document_id cannot be empty.")

    normalized_request_id = _normalize_uuid(request_id)

    logger.info(
        "Starting agricultural document processing",
        extra={
            "message_id": message_id,
            "document_id": document_id,
            "request_id": (
                str(normalized_request_id)
                if normalized_request_id
                else None
            ),
            "document_type": document_type,
            "task_id": self.request.id,
        },
    )

    try:
        result = _build_processing_envelope(
            message_id=message_id,
            document_id=document_id,
            request_id=normalized_request_id,
            document_type=document_type,
            metadata=metadata or {},
        )
    except DocumentTaskError:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected agricultural document processing failure",
            extra={
                "message_id": message_id,
                "document_id": document_id,
            },
        )

        raise DocumentTaskError(
            "Document processing failed."
        ) from exc

    logger.info(
        "Agricultural document processing accepted",
        extra={
            "message_id": message_id,
            "document_id": document_id,
        },
    )

    return result


def _build_processing_envelope(
    *,
    message_id: str,
    document_id: str,
    request_id: UUID | None,
    document_type: str | None,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the internal document-processing envelope.

    Actual document validation, extraction, OCR, structured-data
    parsing, chunking, and embedding belong to packages/documents
    and packages/rag.
    """

    return {
        "status": "accepted",
        "message_id": message_id,
        "document_id": document_id,
        "request_id": (
            str(request_id)
            if request_id is not None
            else None
        ),
        "document_type": document_type,
        "metadata_present": bool(metadata),
    }


def _normalize_uuid(
    value: str | None,
) -> UUID | None:
    if value is None or not value.strip():
        return None

    try:
        return UUID(value)
    except ValueError as exc:
        raise DocumentTaskError(
            "request_id must be a valid UUID."
        ) from exc


__all__ = [
    "DocumentProcessingTask",
    "DocumentTaskError",
    "process_document",
]