from __future__ import annotations

from datetime import datetime, timezone


def run_sustainability_check() -> dict[str, str]:
    """
    Check active farms for sustainability metrics and impact updates.

    The scheduler only triggers the job.
    Sustainability calculations belong to the sustainability and
    optimization layers.
    """

    started_at = datetime.now(timezone.utc)

    return {
        "job": "sustainability",
        "status": "scheduled",
        "started_at": started_at.isoformat(),
    }


__all__ = [
    "run_sustainability_check",
]