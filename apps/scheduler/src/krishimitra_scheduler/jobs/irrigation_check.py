from __future__ import annotations

from datetime import datetime, timezone


def run_irrigation_check() -> dict[str, str]:
    """
    Check active farms for irrigation-related conditions.

    The scheduler owns execution timing only.
    Irrigation calculations and recommendations belong to the
    irrigation/ML/decision-engine layers.
    """

    started_at = datetime.now(timezone.utc)

    return {
        "job": "irrigation_check",
        "status": "scheduled",
        "started_at": started_at.isoformat(),
    }


__all__ = [
    "run_irrigation_check",
]