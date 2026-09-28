from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from celery import Task

from krishimitra_worker.celery_app import celery_app

logger = logging.getLogger(__name__)


class SpeechTaskError(RuntimeError):
    """Raised when speech processing fails."""


class SpeechProcessingTask(Task):
    """
    Base Celery task for speech-processing workloads.

    Speech inference can be expensive, so it runs asynchronously
    outside the WhatsApp webhook request lifecycle.
    """

    autoretry_for = (SpeechTaskError,)
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    max_retries = 5


@celery_app.task(
    bind=True,
    base=SpeechProcessingTask,
    name="krishimitra_worker.tasks.speech.process_audio",
)
def process_audio(
    self: SpeechProcessingTask,
    *,
    message_id: str,
    media_id: str,
    request_id: str | None = None,
    language: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Process an incoming agricultural voice message asynchronously.

    The task receives references to persisted media rather than raw
    audio bytes. Actual downloading, transcription, language handling,
    and AI orchestration remain owned by their respective packages.
    """

    if not message_id.strip():
        raise SpeechTaskError("message_id cannot be empty.")

    if not media_id.strip():
        raise SpeechTaskError("media_id cannot be empty.")

    normalized_request_id = _normalize_uuid(request_id)

    logger.info(
        "Starting speech processing",
        extra={
            "message_id": message_id,
            "media_id": media_id,
            "request_id": (
                str(normalized_request_id)
                if normalized_request_id
                else None
            ),
            "language": language,
            "task_id": self.request.id,
        },
    )

    try:
        result = _build_processing_envelope(
            message_id=message_id,
            media_id=media_id,
            request_id=normalized_request_id,
            language=language,
            metadata=metadata or {},
        )
    except SpeechTaskError:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected speech processing failure",
            extra={
                "message_id": message_id,
                "media_id": media_id,
            },
        )

        raise SpeechTaskError(
            "Speech processing failed."
        ) from exc

    logger.info(
        "Speech processing accepted",
        extra={
            "message_id": message_id,
            "media_id": media_id,
        },
    )

    return result


def _build_processing_envelope(
    *,
    message_id: str,
    media_id: str,
    request_id: UUID | None,
    language: str | None,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Create the internal processing envelope.

    No transcription is performed here. The actual speech model
    belongs to packages/speech and will be connected when the
    speech service layer is implemented.
    """

    return {
        "status": "accepted",
        "message_id": message_id,
        "media_id": media_id,
        "request_id": (
            str(request_id)
            if request_id is not None
            else None
        ),
        "language": language,
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
        raise SpeechTaskError(
            "request_id must be a valid UUID."
        ) from exc


__all__ = [
    "SpeechProcessingTask",
    "SpeechTaskError",
    "process_audio",
]