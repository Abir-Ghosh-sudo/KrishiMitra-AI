"""Irrigation window detection from weather forecasts.

Identifies optimal irrigation windows based on:
- Expected rainfall (skip if >5 mm forecast)
- Wind speed (avoid drift above 20 km/h)
- Temperature (avoid peak heat)
- Evapotranspiration demand (ET0) for scheduling volume
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Sequence

from ..models import DailyForecast, HourlyForecast

__all__ = [
    "IrrigationRecommendation",
    "IrrigationWindow",
    "IrrigationWindowFinder",
    "IrrigationWindowStatus",
]

logger = logging.getLogger(__name__)


class IrrigationWindowStatus(StrEnum):
    OPTIMAL = "optimal"
    SUBOPTIMAL = "suboptimal"
    NOT_RECOMMENDED = "not_recommended"
    SKIP_RAIN = "skip_rain"


@dataclass(frozen=True)
class IrrigationWindow:
    """A candidate irrigation window."""

    start: datetime
    end: datetime
    status: IrrigationWindowStatus
    reason: str
    wind_speed_kmh: float
    temperature_c: float
    precipitation_expected_mm: float


@dataclass(frozen=True)
class IrrigationRecommendation:
    """Full irrigation recommendation for a forecast period."""

    windows: list[IrrigationWindow]
    et0_total_mm: float
    rainfall_expected_mm: float
    net_irrigation_need_mm: float
    skip_irrigation: bool
    summary: str

    @property
    def best_windows(self) -> list[IrrigationWindow]:
        return [w for w in self.windows if w.status == IrrigationWindowStatus.OPTIMAL]


class IrrigationWindowFinder:
    """Finds optimal irrigation windows from hourly/daily forecasts.

    Parameters
    ----------
    rain_skip_mm:
        Skip irrigation if expected rainfall exceeds this (default 5 mm).
    max_wind_kmh:
        Maximum wind speed for sprinkler irrigation (default 20 km/h).
    peak_heat_hour_start:
        Start of peak heat window to avoid (default 10 = 10 AM).
    peak_heat_hour_end:
        End of peak heat window to avoid (default 16 = 4 PM).
    """

    def __init__(
        self,
        *,
        rain_skip_mm: float = 5.0,
        max_wind_kmh: float = 20.0,
        peak_heat_hour_start: int = 10,
        peak_heat_hour_end: int = 16,
    ) -> None:
        self._rain_skip_mm = rain_skip_mm
        self._max_wind = max_wind_kmh
        self._peak_start = peak_heat_hour_start
        self._peak_end = peak_heat_hour_end

    def find(
        self,
        daily_forecasts: Sequence[DailyForecast],
    ) -> IrrigationRecommendation:
        """Compute irrigation windows from forecast days."""
        total_et0 = sum(d.et0_mm or 0.0 for d in daily_forecasts)
        total_rain = sum(d.precipitation_mm for d in daily_forecasts)
        net_need = max(0.0, total_et0 - total_rain)

        windows: list[IrrigationWindow] = []

        for day in daily_forecasts:
            if day.hourly:
                windows.extend(self._hourly_windows(day))
            else:
                windows.extend(self._daily_windows(day))

        skip = total_rain >= self._rain_skip_mm * len(daily_forecasts)

        summary = self._build_summary(net_need, total_rain, skip, windows)
        return IrrigationRecommendation(
            windows=windows,
            et0_total_mm=round(total_et0, 1),
            rainfall_expected_mm=round(total_rain, 1),
            net_irrigation_need_mm=round(net_need, 1),
            skip_irrigation=skip,
            summary=summary,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _hourly_windows(self, day: DailyForecast) -> list[IrrigationWindow]:
        windows: list[IrrigationWindow] = []

        for i, hour in enumerate(day.hourly):
            h = hour.timestamp.hour
            # Only consider 05:00–08:00 and 17:00–20:00
            if not (5 <= h <= 8 or 17 <= h <= 20):
                continue

            # Need at least 2 consecutive hours for a window
            if i + 1 >= len(day.hourly):
                continue
            next_hour = day.hourly[i + 1]

            rain_sum = hour.precipitation_mm + next_hour.precipitation_mm
            wind = max(hour.wind_speed_kmh, next_hour.wind_speed_kmh)
            temp = hour.temperature_c

            status, reason = self._evaluate_slot(rain_sum, wind, temp, h)

            windows.append(
                IrrigationWindow(
                    start=hour.timestamp,
                    end=next_hour.timestamp,
                    status=status,
                    reason=reason,
                    wind_speed_kmh=wind,
                    temperature_c=temp,
                    precipitation_expected_mm=rain_sum,
                )
            )

        return windows

    def _daily_windows(self, day: DailyForecast) -> list[IrrigationWindow]:
        """Fallback when hourly data is unavailable — recommend morning slot."""
        from datetime import time, timezone

        morning_start = datetime.combine(
            day.date, time(6, 0), tzinfo=timezone.utc
        )
        morning_end = datetime.combine(
            day.date, time(8, 0), tzinfo=timezone.utc
        )

        if day.precipitation_mm >= self._rain_skip_mm:
            status = IrrigationWindowStatus.SKIP_RAIN
            reason = f"Rain expected ({day.precipitation_mm:.1f} mm) — skip irrigation."
        elif day.wind_speed_max_kmh > self._max_wind:
            status = IrrigationWindowStatus.NOT_RECOMMENDED
            reason = f"High winds ({day.wind_speed_max_kmh:.0f} km/h) — drift risk."
        else:
            status = IrrigationWindowStatus.SUBOPTIMAL
            reason = "Hourly data unavailable; estimated morning window."

        return [
            IrrigationWindow(
                start=morning_start,
                end=morning_end,
                status=status,
                reason=reason,
                wind_speed_kmh=day.wind_speed_max_kmh,
                temperature_c=day.temp_min_c,
                precipitation_expected_mm=day.precipitation_mm,
            )
        ]

    def _evaluate_slot(
        self,
        rain_mm: float,
        wind_kmh: float,
        temp_c: float,
        hour: int,
    ) -> tuple[IrrigationWindowStatus, str]:
        if rain_mm >= self._rain_skip_mm:
            return (
                IrrigationWindowStatus.SKIP_RAIN,
                f"Rain forecast ({rain_mm:.1f} mm); irrigation not needed.",
            )
        if wind_kmh > self._max_wind:
            return (
                IrrigationWindowStatus.NOT_RECOMMENDED,
                f"Wind too strong ({wind_kmh:.0f} km/h); sprinkler drift risk.",
            )
        if self._peak_start <= hour < self._peak_end:
            return (
                IrrigationWindowStatus.NOT_RECOMMENDED,
                "Peak heat hours; high evaporation loss.",
            )
        if 5 <= hour <= 8 or 18 <= hour <= 20:
            return (
                IrrigationWindowStatus.OPTIMAL,
                "Early morning/evening slot; low evaporation, good infiltration.",
            )
        return (
            IrrigationWindowStatus.SUBOPTIMAL,
            "Acceptable window but not ideal for water efficiency.",
        )

    @staticmethod
    def _build_summary(
        net_need: float,
        total_rain: float,
        skip: bool,
        windows: list[IrrigationWindow],
    ) -> str:
        if skip:
            return (
                f"Sufficient rainfall expected ({total_rain:.1f} mm). "
                "No irrigation required for this period."
            )
        best = [w for w in windows if w.status == IrrigationWindowStatus.OPTIMAL]
        if not best:
            return (
                f"Net irrigation need: {net_need:.1f} mm. "
                "No ideal windows found; use early morning if necessary."
            )
        return (
            f"Net irrigation need: {net_need:.1f} mm. "
            f"{len(best)} optimal window(s) found. "
            "Irrigate during early morning or evening hours."
        )
