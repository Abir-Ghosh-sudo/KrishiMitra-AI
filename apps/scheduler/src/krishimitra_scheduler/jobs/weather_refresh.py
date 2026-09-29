from __future__ import annotations

from datetime import datetime, timezone


def refresh_weather_data() -> dict[str, str]:
    """
    Refresh weather data for active farms.

    The scheduler only defines the job boundary here.
    Actual weather fetching and persistence belong to the weather/database
    service layers and will be connected when those packages are implemented.
    """

    started_at = datetime.now(timezone.utc)

    return {
        "job": "weather_refresh",
        "status": "scheduled",
        "started_at": started_at.isoformat(),
    }


__all__ = [
    "refresh_weather_data",
]