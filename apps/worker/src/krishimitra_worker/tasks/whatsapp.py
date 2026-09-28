from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from celery import Task

from krishimitra_worker.celery_app import celery_app

logger = logging.getLogger(__name__)


class WhatsAppTaskError(RuntimeError):
    """Raised when WhatsApp background processing fails."""


class WhatsAppProcessingTask(Task):
    """
    Base task for WhatsApp processing.

    Retries are handled by Celery rather than by the webhook layer.
    This keeps the webhook fast and prevents duplicate retry logic.
    """

    autoretry_for = (WhatsAppTaskError,)
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    max_retries = 5


@celery_app.task(
    bind=True,
    base=WhatsAppProcessingTask,
    name="krishimitra_worker.tasks.whatsapp.process_message",
)
def process_whatsapp_message(
    self: WhatsAppProcessingTask,
    *,
    message_id: str,
    request_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Process a persisted WhatsApp message asynchronously.

    The webhook must persist and enqueue the message before this task
    executes. Heavy AI/ML processing belongs behind this boundary.
    """

    if not message_id.strip():
        raise WhatsAppTaskError(
            "message_id cannot be empty."
        )

    normalized_request_id = _normalize_uuid(
        request_id
    )

    logger.info(
        "Starting WhatsApp message processing",
        extra={
            "message_id": message_id,
            "request_id": (
                str(normalized_request_id)
                if normalized_request_id
                else None
            ),
            "task_id": self.request.id,
        },
    )

    try:
        result = _dispatch_message(
            message_id=message_id,
            request_id=normalized_request_id,
            payload=payload or {},
        )
    except WhatsAppTaskError:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected WhatsApp processing failure",
            extra={
                "message_id": message_id,
                "request_id": (
                    str(normalized_request_id)
                    if normalized_request_id
                    else None
                ),
            },
        )

        raise WhatsAppTaskError(
            "WhatsApp message processing failed."
        ) from exc

    logger.info(
        "Completed WhatsApp message processing",
        extra={
            "message_id": message_id,
            "request_id": (
                str(normalized_request_id)
                if normalized_request_id
                else None
            ),
        },
    )

    return result


def _dispatch_message(
    *,
    message_id: str,
    request_id: UUID | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the processing envelope.

    Actual persistence lookup, multimodal routing, AI orchestration,
    and response delivery will be injected through their respective
    service packages. This task must remain an orchestration boundary,
    not a second implementation of those services.
    """

    return {
        "status": "accepted",
        "message_id": message_id,
        "request_id": (
            str(request_id)
            if request_id is not None
            else None
        ),
        "payload_present": bool(payload),
    }


def _normalize_uuid(
    value: str | None,
) -> UUID | None:
    if value is None:
        return None

    if not value.strip():
        return None

    try:
        return UUID(value)
    except ValueError as exc:
        raise WhatsAppTaskError(
            "request_id must be a valid UUID."
        ) from exc


__all__ = [
    "WhatsAppProcessingTask",
    "WhatsAppTaskError",
    "process_whatsapp_message",
]