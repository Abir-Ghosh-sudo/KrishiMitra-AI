from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from celery import Task

from krishimitra_worker.celery_app import celery_app

logger = logging.getLogger(__name__)


class PredictionTaskError(RuntimeError):
    """Raised when a prediction task cannot be processed."""


class PredictionProcessingTask(Task):
    """
    Base Celery task for ML prediction workloads.

    Prediction jobs are executed asynchronously because inference may
    require feature construction, model loading, database context,
    or multiple model calls.
    """

    autoretry_for = (PredictionTaskError,)
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    max_retries = 5


@celery_app.task(
    bind=True,
    base=PredictionProcessingTask,
    name="krishimitra_worker.tasks.predictions.run_prediction",
)
def run_prediction(
    self: PredictionProcessingTask,
    *,
    prediction_id: str,
    prediction_type: str,
    farm_id: str,
    request_id: str | None = None,
    crop_id: str | None = None,
    feature_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute an asynchronous ML prediction request.

    Parameters
    ----------
    prediction_id:
        Persisted prediction/job identifier.

    prediction_type:
        Type of prediction requested, for example:

        - disease_risk
        - pest_risk
        - irrigation
        - yield
        - energy
        - crop_stage

    farm_id:
        Farm against which the prediction is evaluated.

    request_id:
        Correlation identifier for the complete request.

    crop_id:
        Optional crop context.

    feature_context:
        Persisted or precomputed feature context. Large datasets should
        be referenced by ID rather than passed through Celery.
    """

    if not prediction_id.strip():
        raise PredictionTaskError(
            "prediction_id cannot be empty."
        )

    if not prediction_type.strip():
        raise PredictionTaskError(
            "prediction_type cannot be empty."
        )

    if not farm_id.strip():
        raise PredictionTaskError(
            "farm_id cannot be empty."
        )

    normalized_request_id = _normalize_uuid(request_id)

    logger.info(
        "Starting ML prediction",
        extra={
            "prediction_id": prediction_id,
            "prediction_type": prediction_type,
            "farm_id": farm_id,
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
        result = _build_prediction_envelope(
            prediction_id=prediction_id,
            prediction_type=prediction_type,
            farm_id=farm_id,
            crop_id=crop_id,
            request_id=normalized_request_id,
            feature_context=feature_context or {},
        )
    except PredictionTaskError:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected ML prediction failure",
            extra={
                "prediction_id": prediction_id,
                "prediction_type": prediction_type,
                "farm_id": farm_id,
            },
        )

        raise PredictionTaskError(
            "ML prediction failed."
        ) from exc

    logger.info(
        "ML prediction accepted",
        extra={
            "prediction_id": prediction_id,
            "prediction_type": prediction_type,
        },
    )

    return result


def _build_prediction_envelope(
    *,
    prediction_id: str,
    prediction_type: str,
    farm_id: str,
    crop_id: str | None,
    request_id: UUID | None,
    feature_context: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the internal prediction-processing envelope.

    Actual feature construction, model selection, inference,
    uncertainty estimation, model-version tracking, and persistence
    belong to the ML/service layers.
    """

    return {
        "status": "accepted",
        "prediction_id": prediction_id,
        "prediction_type": prediction_type,
        "farm_id": farm_id,
        "crop_id": crop_id,
        "request_id": (
            str(request_id)
            if request_id is not None
            else None
        ),
        "feature_context_present": bool(feature_context),
    }


def _normalize_uuid(
    value: str | None,
) -> UUID | None:
    if value is None or not value.strip():
        return None

    try:
        return UUID(value)
    except ValueError as exc:
        raise PredictionTaskError(
            "request_id must be a valid UUID."
        ) from exc


__all__ = [
    "PredictionProcessingTask",
    "PredictionTaskError",
    "run_prediction",
]