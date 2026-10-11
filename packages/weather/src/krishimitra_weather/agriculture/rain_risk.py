"""Rainfall risk assessment for agricultural operations.

Classifies rain events by intensity, identifies risks for harvesting,
sowing, and field operations, and computes waterlogging probability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence

from ..models import DailyForecast

__all__ = [
    "RainIntensity",
    "RainRiskAssessor",
    "RainRiskReport",
    "RainfallEvent",
]

logger = logging.getLogger(__name__)


class RainIntensity(StrEnum):
    NONE = "none"
    TRACE = "trace"          # < 2.5 mm
    LIGHT = "light"          # 2.5–7.5 mm
    MODERATE = "moderate"    # 7.5–35.5 mm
    HEAVY = "heavy"          # 35.5–64.4 mm
    VERY_HEAVY = "very_heavy"  # 64.4–124.4 mm
    EXTREMELY_HEAVY = "extremely_heavy"  # > 124.4 mm


@dataclass(frozen=True)
class RainfallEvent:
    """A single-day rain event."""

    date_str: str
    amount_mm: float
    intensity: RainIntensity
    probability_pct: float
    operation_impact: str


@dataclass(frozen=True)
class RainRiskReport:
    """Full rainfall risk assessment."""

    events: list[RainfallEvent]
    total_rain_mm: float
    max_daily_mm: float
    rainy_days: int
    waterlogging_risk: bool
    harvest_risk: bool
    sowing_risk: bool
    flood_alert: bool
    summary: str

    @property
    def high_intensity_events(self) -> list[RainfallEvent]:
        return [
            e for e in self.events
            if e.intensity in (
                RainIntensity.HEAVY,
                RainIntensity.VERY_HEAVY,
                RainIntensity.EXTREMELY_HEAVY,
            )
        ]


def _classify_intensity(mm: float) -> RainIntensity:
    if mm == 0:
        return RainIntensity.NONE
    if mm < 2.5:
        return RainIntensity.TRACE
    if mm < 7.5:
        return RainIntensity.LIGHT
    if mm < 35.5:
        return RainIntensity.MODERATE
    if mm < 64.4:
        return RainIntensity.HEAVY
    if mm < 124.4:
        return RainIntensity.VERY_HEAVY
    return RainIntensity.EXTREMELY_HEAVY


def _operation_impact(intensity: RainIntensity) -> str:
    impacts = {
        RainIntensity.NONE: "No impact on field operations.",
        RainIntensity.TRACE: "Negligible impact; field operations can continue.",
        RainIntensity.LIGHT: "Minor impact; most operations can proceed with caution.",
        RainIntensity.MODERATE: "Delay sowing/harvesting; machinery operation may be hampered.",
        RainIntensity.HEAVY: "Suspend all field operations; waterlogging risk in low-lying areas.",
        RainIntensity.VERY_HEAVY: "High flood risk; evacuate low-lying farm areas.",
        RainIntensity.EXTREMELY_HEAVY: "EXTREME FLOOD RISK — immediate safety action required.",
    }
    return impacts.get(intensity, "Unknown impact.")


class RainRiskAssessor:
    """Assesses rainfall risks for agricultural operations.

    Parameters
    ----------
    waterlogging_threshold_mm:
        Cumulative rain (mm) over forecast period above which waterlogging
        risk is flagged (default 50 mm).
    harvest_risk_mm:
        Single-day rain above which harvesting is not recommended (default 5 mm).
    flood_alert_mm:
        Single-day rain above which flood alert is triggered (default 64.4 mm).
    """

    def __init__(
        self,
        *,
        waterlogging_threshold_mm: float = 50.0,
        harvest_risk_mm: float = 5.0,
        flood_alert_mm: float = 64.4,
    ) -> None:
        self._waterlogging_thresh = waterlogging_threshold_mm
        self._harvest_risk_mm = harvest_risk_mm
        self._flood_alert_mm = flood_alert_mm

    def assess(self, daily_forecasts: Sequence[DailyForecast]) -> RainRiskReport:
        events: list[RainfallEvent] = []
        total = 0.0
        max_daily = 0.0

        for day in daily_forecasts:
            intensity = _classify_intensity(day.precipitation_mm)
            events.append(
                RainfallEvent(
                    date_str=str(day.date),
                    amount_mm=day.precipitation_mm,
                    intensity=intensity,
                    probability_pct=day.precipitation_probability_pct,
                    operation_impact=_operation_impact(intensity),
                )
            )
            total += day.precipitation_mm
            max_daily = max(max_daily, day.precipitation_mm)

        rainy_days = sum(1 for e in events if e.amount_mm > 2.5)
        waterlogging = total >= self._waterlogging_thresh
        harvest_risk = any(e.amount_mm >= self._harvest_risk_mm for e in events)
        sowing_risk = rainy_days >= 3 or total > 30
        flood_alert = max_daily >= self._flood_alert_mm

        summary = self._build_summary(
            total, max_daily, rainy_days, waterlogging, flood_alert
        )

        return RainRiskReport(
            events=events,
            total_rain_mm=round(total, 1),
            max_daily_mm=round(max_daily, 1),
            rainy_days=rainy_days,
            waterlogging_risk=waterlogging,
            harvest_risk=harvest_risk,
            sowing_risk=sowing_risk,
            flood_alert=flood_alert,
            summary=summary,
        )

    @staticmethod
    def _build_summary(
        total: float,
        max_daily: float,
        rainy_days: int,
        waterlogging: bool,
        flood_alert: bool,
    ) -> str:
        parts: list[str] = [
            f"Total expected rainfall: {total:.1f} mm over {rainy_days} rainy day(s)."
        ]
        if flood_alert:
            parts.append(
                f"⚠️ FLOOD ALERT: {max_daily:.0f} mm expected in a single day. "
                "Protect crops, equipment, and livestock immediately."
            )
        elif waterlogging:
            parts.append(
                "Waterlogging risk in poorly-drained fields. "
                "Ensure drainage channels are clear before rain."
            )
        elif total < 5:
            parts.append("Dry conditions expected. Plan irrigation accordingly.")
        return " ".join(parts)
