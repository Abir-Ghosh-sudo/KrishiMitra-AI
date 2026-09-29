from __future__ import annotations

from datetime import datetime, timezone


def run_disease_risk_check() -> dict[str, str]:
    """
    Check active farms for weather-driven disease risk.

    The scheduler is responsible only for triggering the job.
    Disease-risk inference belongs to the ML and decision-engine layers.
    """

    started_at = datetime.now(timezone.utc)

    return {
        "job": "disease_risk",
        "status": "scheduled",
        "started_at": started_at.isoformat(),
    }


__all__ = [
    "run_disease_risk_check",
]