"""Spray window detection for pesticide/fungicide/fertiliser applications.

Identifies hourly windows that satisfy all agrochemical label conditions:
- Wind speed ≤ 15 km/h (drift control)
- No rain in the window or within 2 hours after
- Temperature 15–32°C (efficacy range)
- Relative humidity 40–90% (label requirement)
- Not peak heat (avoid rapid evaporation of spray droplets)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Sequence

from ..models import DailyForecast, HourlyForecast

__all__ = [
    "SprayCondition",
    "SprayWindow",
    "SprayWindowFinder",
    "SprayWindowReport",
]

logger = logging.getLogger(__name__)

# Agrochemical application parameter bounds
_MAX_WIND_KMPH = 15.0
_MIN_TEMP_C = 15.0
_MAX_TEMP_C = 32.0
_MIN_RH_PCT = 40.0
_MAX_RH_PCT = 90.0
_RAIN_BUFFER_MM = 0.5  # ignore trace rainfall
_POST_SPRAY_RAIN_HOURS = 2  # rain-free period after spraying


class SprayCondition(StrEnum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MARGINAL = "marginal"
    UNSUITABLE = "unsuitable"


@dataclass(frozen=True)
class SprayWindow:
    """A candidate spray window."""

    start: datetime
    end: datetime
    condition: SprayCondition
    wind_speed_kmh: float
    temperature_c: float
    humidity_pct: float
    inversion_risk: bool  # temperature inversion = drift risk
    reasons: list[str]


@dataclass(frozen=True)
class SprayWindowReport:
    """Complete spray timing report for a forecast period."""

    windows: list[SprayWindow]
    total_suitable_hours: int
    best_day: str | None
    advisory: str

    @property
    def excellent_windows(self) -> list[SprayWindow]:
        return [w for w in self.windows if w.condition == SprayCondition.EXCELLENT]

    @property
    def good_or_better(self) -> list[SprayWindow]:
        return [
            w for w in self.windows
            if w.condition in (SprayCondition.EXCELLENT, SprayCondition.GOOD)
        ]


class SprayWindowFinder:
    """Finds safe pesticide/fertiliser spray windows from hourly forecasts.

    Parameters
    ----------
    max_wind_kmh:
        Maximum wind speed (default 15 km/h per most label requirements).
    min_temp_c / max_temp_c:
        Temperature bounds for spray efficacy.
    min_rh_pct / max_rh_pct:
        Humidity bounds (too dry = rapid evaporation; too humid = poor coverage).
    """

    def __init__(
        self,
        *,
        max_wind_kmh: float = _MAX_WIND_KMPH,
        min_temp_c: float = _MIN_TEMP_C,
        max_temp_c: float = _MAX_TEMP_C,
        min_rh_pct: float = _MIN_RH_PCT,
        max_rh_pct: float = _MAX_RH_PCT,
    ) -> None:
        self._max_wind = max_wind_kmh
        self._min_temp = min_temp_c
        self._max_temp = max_temp_c
        self._min_rh = min_rh_pct
        self._max_rh = max_rh_pct

    def find(
        self,
        daily_forecasts: Sequence[DailyForecast],
    ) -> SprayWindowReport:
        all_windows: list[SprayWindow] = []

        for day in daily_forecasts:
            if day.hourly:
                all_windows.extend(self._assess_hourly(day.hourly))

        suitable = [
            w for w in all_windows
            if w.condition in (SprayCondition.EXCELLENT, SprayCondition.GOOD)
        ]
        best_day = self._best_day(suitable)
        advisory = self._build_advisory(all_windows, suitable)

        return SprayWindowReport(
            windows=all_windows,
            total_suitable_hours=len(suitable),
            best_day=best_day,
            advisory=advisory,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _assess_hourly(
        self, hours: Sequence[HourlyForecast]
    ) -> list[SprayWindow]:
        windows: list[SprayWindow] = []
        hour_list = list(hours)

        for i, hour in enumerate(hour_list):
            h = hour.timestamp.hour
            # Only daytime hours (6 AM – 7 PM)
            if not (6 <= h <= 19):
                continue

            reasons: list[str] = []
            unsuitable = False

            # Wind check
            if hour.wind_speed_kmh > self._max_wind:
                reasons.append(f"Wind {hour.wind_speed_kmh:.0f} km/h > {self._max_wind} km/h limit")
                unsuitable = True

            # Temperature check
            if not (self._min_temp <= hour.temperature_c <= self._max_temp):
                reasons.append(
                    f"Temperature {hour.temperature_c:.1f}°C out of range "
                    f"[{self._min_temp}–{self._max_temp}°C]"
                )
                unsuitable = True

            # Humidity check
            if not (self._min_rh <= hour.humidity_pct <= self._max_rh):
                reasons.append(
                    f"Humidity {hour.humidity_pct:.0f}% out of range "
                    f"[{self._min_rh}–{self._max_rh}%]"
                )
                unsuitable = True

            # Rain check — current + next 2 hours
            rain_window = sum(
                hour_list[j].precipitation_mm
                for j in range(i, min(i + _POST_SPRAY_RAIN_HOURS + 1, len(hour_list)))
            )
            if rain_window > _RAIN_BUFFER_MM:
                reasons.append(
                    f"Rain expected within {_POST_SPRAY_RAIN_HOURS} h "
                    f"({rain_window:.1f} mm)"
                )
                unsuitable = True

            # Temperature inversion risk (early morning stable air)
            inversion = h < 8 and hour.wind_speed_kmh < 5

            if unsuitable:
                condition = SprayCondition.UNSUITABLE
            elif inversion:
                condition = SprayCondition.MARGINAL
                reasons.append("Possible temperature inversion; spray may drift.")
            elif hour.wind_speed_kmh < 8 and self._min_temp + 3 <= hour.temperature_c <= self._max_temp - 5:
                condition = SprayCondition.EXCELLENT
            else:
                condition = SprayCondition.GOOD

            # End time = next hour slot
            end_ts = hour_list[i + 1].timestamp if i + 1 < len(hour_list) else hour.timestamp

            windows.append(
                SprayWindow(
                    start=hour.timestamp,
                    end=end_ts,
                    condition=condition,
                    wind_speed_kmh=hour.wind_speed_kmh,
                    temperature_c=hour.temperature_c,
                    humidity_pct=hour.humidity_pct,
                    inversion_risk=inversion,
                    reasons=reasons,
                )
            )

        return windows

    @staticmethod
    def _best_day(suitable: list[SprayWindow]) -> str | None:
        if not suitable:
            return None
        from collections import Counter
        counts = Counter(w.start.date().isoformat() for w in suitable)
        return counts.most_common(1)[0][0]

    @staticmethod
    def _build_advisory(
        all_windows: list[SprayWindow],
        suitable: list[SprayWindow],
    ) -> str:
        if not all_windows:
            return "Hourly data unavailable. Apply pesticides in early morning or evening when wind is calm."
        if not suitable:
            return (
                "No suitable spray windows found in the forecast period. "
                "Conditions are either too windy, too wet, or temperatures are out of range. "
                "Monitor the 10-day outlook before planning applications."
            )
        excellent = [w for w in suitable if w.condition == SprayCondition.EXCELLENT]
        return (
            f"{len(suitable)} suitable window(s) found "
            f"({len(excellent)} excellent). "
            "Best practice: spray when wind < 15 km/h, temp 18–28°C, humidity 50–80%. "
            "Always read product label before applying."
        )
