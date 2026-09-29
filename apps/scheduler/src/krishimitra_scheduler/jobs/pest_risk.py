from __future__ import annotations

from datetime import datetime, timezone


def run_pest_risk_check() -> dict[str, str]:
    """
    Check active farms for weather- and crop-driven pest risk.

    The scheduler only triggers the job.
    Pest-risk prediction belongs to the ML and decision-engine layers.
    """

    started_at = datetime.now(timezone.utc)

    return {
        "job": "pest_risk",
        "status": "scheduled",
        "started_at": started_at.isoformat(),
    }


__all__ = [
    "run_pest_risk_check",
]