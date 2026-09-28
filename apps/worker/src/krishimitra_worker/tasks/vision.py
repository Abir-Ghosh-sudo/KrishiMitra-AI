from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from celery import Task

from krishimitra_worker.celery_app import celery_app

logger = logging.getLogger(__name__)


class VisionTaskError(RuntimeError):
    """Raised when vision processing fails."""


class VisionProcessingTask(Task):
    """
    Base Celery task for agricultural vision workloads.

    Image processing and ML inference are intentionally executed
    asynchronously so the WhatsApp webhook remains lightweight.
    """

    autoretry_for = (VisionTaskError,)
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    max_retries = 5


@celery_app.task(
    bind=True,
    base=VisionProcessingTask,
    name="krishimitra_worker.tasks.vision.process_images",
)
def process_images(
    self: VisionProcessingTask,
    *,
    message_id: str,
    media_ids: list[str],
    request_id: str | None = None,
    crop: str | None = None,
    crop_stage: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Process one or more agricultural images asynchronously.

    Parameters
    ----------
    message_id:
        Persisted WhatsApp message identifier.

    media_ids:
        References to persisted image objects. Raw image bytes should
        not be passed through the Celery message.

    request_id:
        Correlation identifier for tracing the complete request.

    crop:
        Optional farmer-provided crop context.

    crop_stage:
        Optional crop growth-stage context.

    metadata:
        Additional non-sensitive processing metadata.
    """

    if not message_id.strip():
        raise VisionTaskError("message_id cannot be empty.")

    if not media_ids:
        raise VisionTaskError(
            "At least one media_id is required."
        )

    normalized_media_ids = [
        media_id.strip()
        for media_id in media_ids
        if media_id and media_id.strip()
    ]

    if not normalized_media_ids:
        raise VisionTaskError(
            "At least one valid media_id is required."
        )

    normalized_request_id = _normalize_uuid(request_id)

    logger.info(
        "Starting agricultural vision processing",
        extra={
            "message_id": message_id,
            "media_count": len(normalized_media_ids),
            "request_id": (
                str(normalized_request_id)
                if normalized_request_id
                else None
            ),
            "crop": crop,
            "crop_stage": crop_stage,
            "task_id": self.request.id,
        },
    )

    try:
        result = _build_processing_envelope(
            message_id=message_id,
            media_ids=normalized_media_ids,
            request_id=normalized_request_id,
            crop=crop,
            crop_stage=crop_stage,
            metadata=metadata or {},
        )
    except VisionTaskError:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected agricultural vision processing failure",
            extra={
                "message_id": message_id,
                "media_count": len(normalized_media_ids),
            },
        )

        raise VisionTaskError(
            "Vision processing failed."
        ) from exc

    logger.info(
        "Agricultural vision processing accepted",
        extra={
            "message_id": message_id,
            "media_count": len(normalized_media_ids),
        },
    )

    return result


def _build_processing_envelope(
    *,
    message_id: str,
    media_ids: list[str],
    request_id: UUID | None,
    crop: str | None,
    crop_stage: str | None,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the internal vision-processing envelope.

    Actual image validation, preprocessing, vision inference,
    disease/pest classification, confidence evaluation, and expert
    escalation belong to the dedicated vision/ML services.
    """

    return {
        "status": "accepted",
        "message_id": message_id,
        "media_ids": tuple(media_ids),
        "media_count": len(media_ids),
        "request_id": (
            str(request_id)
            if request_id is not None
            else None
        ),
        "crop": crop,
        "crop_stage": crop_stage,
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
        raise VisionTaskError(
            "request_id must be a valid UUID."
        ) from exc


__all__ = [
    "VisionProcessingTask",
    "VisionTaskError",
    "process_images",
]