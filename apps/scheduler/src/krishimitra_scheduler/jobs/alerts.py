from __future__ import annotations

from datetime import datetime, timezone


def run_alert_generation() -> dict[str, str]:
    """
    Generate pending farm alerts.

    The scheduler is responsible only for triggering the job.
    Alert evaluation, prioritization, and delivery belong to the
    alerts, decision-engine, and WhatsApp layers.
    """

    started_at = datetime.now(timezone.utc)

    return {
        "job": "alerts",
        "status": "scheduled",
        "started_at": started_at.isoformat(),
    }


__all__ = [
    "run_alert_generation",
]