from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from celery import Task

from krishimitra_worker.celery_app import celery_app

logger = logging.getLogger(__name__)


class AlertTaskError(RuntimeError):
    """Raised when an alert task cannot be processed."""


class AlertProcessingTask(Task):
    """
    Base Celery task for alert workloads.

    Alert generation and delivery are asynchronous so weather,
    disease-risk, irrigation, pest-risk, and other background
    signals never block the webhook or API request lifecycle.
    """

    autoretry_for = (AlertTaskError,)
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    max_retries = 5


@celery_app.task(
    bind=True,
    base=AlertProcessingTask,
    name="krishimitra_worker.tasks.alerts.process_alert",
)
def process_alert(
    self: AlertProcessingTask,
    *,
    alert_id: str,
    farm_id: str,
    alert_type: str,
    request_id: str | None = None,
    crop_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Process a persisted farmer alert asynchronously.

    Examples of alert types include:

    - disease_risk
    - pest_risk
    - heavy_rain
    - heat_stress
    - irrigation
    - spray_window
    - fertilizer_timing
    - weather_change
    - sustainability
    - expert_followup

    The task receives identifiers and compact context only.
    Large payloads or media should remain in persistent storage.
    """

    if not alert_id.strip():
        raise AlertTaskError("alert_id cannot be empty.")

    if not farm_id.strip():
        raise AlertTaskError("farm_id cannot be empty.")

    if not alert_type.strip():
        raise AlertTaskError("alert_type cannot be empty.")

    normalized_request_id = _normalize_uuid(request_id)

    logger.info(
        "Starting farmer alert processing",
        extra={
            "alert_id": alert_id,
            "farm_id": farm_id,
            "alert_type": alert_type,
            "crop_id": crop_id,
            "request_id": (
                str(normalized_request_id)
                if normalized_request_id
                else None
            ),
            "task_id": self.request.id,
        },
    )

    try:
        result = _build_alert_envelope(
            alert_id=alert_id,
            farm_id=farm_id,
            alert_type=alert_type,
            crop_id=crop_id,
            request_id=normalized_request_id,
            context=context or {},
        )
    except AlertTaskError:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected farmer alert processing failure",
            extra={
                "alert_id": alert_id,
                "farm_id": farm_id,
                "alert_type": alert_type,
            },
        )

        raise AlertTaskError(
            "Alert processing failed."
        ) from exc

    logger.info(
        "Farmer alert processing accepted",
        extra={
            "alert_id": alert_id,
            "farm_id": farm_id,
            "alert_type": alert_type,
        },
    )

    return result


def _build_alert_envelope(
    *,
    alert_id: str,
    farm_id: str,
    alert_type: str,
    crop_id: str | None,
    request_id: UUID | None,
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the internal alert-processing envelope.

    Actual alert rules, prioritization, deduplication, safety checks,
    message generation, and WhatsApp delivery belong to their
    respective domain services.
    """

    return {
        "status": "accepted",
        "alert_id": alert_id,
        "farm_id": farm_id,
        "alert_type": alert_type,
        "crop_id": crop_id,
        "request_id": (
            str(request_id)
            if request_id is not None
            else None
        ),
        "context_present": bool(context),
    }


def _normalize_uuid(
    value: str | None,
) -> UUID | None:
    if value is None or not value.strip():
        return None

    try:
        return UUID(value)
    except ValueError as exc:
        raise AlertTaskError(
            "request_id must be a valid UUID."
        ) from exc


__all__ = [
    "AlertProcessingTask",
    "AlertTaskError",
    "process_alert",
]