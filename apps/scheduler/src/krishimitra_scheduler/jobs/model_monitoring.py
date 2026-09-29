from __future__ import annotations

from datetime import datetime, timezone


def run_model_monitoring() -> dict[str, str]:
    """
    Run scheduled ML model monitoring checks.

    The scheduler only triggers the monitoring workflow.
    Actual drift detection, performance evaluation, and model-health
    analysis belong to the ML/observability layers.
    """

    started_at = datetime.now(timezone.utc)

    return {
        "job": "model_monitoring",
        "status": "scheduled",
        "started_at": started_at.isoformat(),
    }


__all__ = [
    "run_model_monitoring",
]