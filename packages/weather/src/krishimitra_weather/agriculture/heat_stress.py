"""Heat stress assessment for crops and livestock.

Computes Heat Stress Index (HSI) and crop-specific thresholds for
common Indian crops (wheat, rice, maize, cotton, vegetables).
Also includes livestock Temperature-Humidity Index (THI).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Sequence

from ..models import DailyForecast

__all__ = [
    "HeatStressAssessor",
    "HeatStressLevel",
    "HeatStressReport",
    "LivestockTHI",
]

logger = logging.getLogger(__name__)


class HeatStressLevel(StrEnum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


@dataclass(frozen=True)
class LivestockTHI:
    """Temperature-Humidity Index for livestock."""

    value: float
    level: HeatStressLevel
    affected_animals: list[str]
    recommendation: str


@dataclass(frozen=True)
class HeatStressReport:
    """Heat stress assessment for a forecast period."""

    level: HeatStressLevel
    max_temp_c: float
    avg_temp_c: float
    stress_days: int  # days exceeding crop threshold
    total_days: int
    affected_crops: list[str]
    livestock_thi: LivestockTHI | None
    recommendations: list[str]

    @property
    def stress_fraction(self) -> float:
        return self.stress_days / self.total_days if self.total_days else 0.0


# ---------------------------------------------------------------------------
# Crop temperature thresholds (°C) — critical max temp
# ---------------------------------------------------------------------------
_CROP_THRESHOLDS: dict[str, float] = {
    "wheat": 30.0,
    "rice": 35.0,
    "maize": 35.0,
    "cotton": 38.0,
    "soybean": 35.0,
    "groundnut": 36.0,
    "tomato": 35.0,
    "onion": 33.0,
    "potato": 30.0,
    "sugarcane": 38.0,
    "mustard": 28.0,
}


def _stress_level(temp_max: float, threshold: float) -> HeatStressLevel:
    excess = temp_max - threshold
    if excess <= 0:
        return HeatStressLevel.NONE
    if excess < 3:
        return HeatStressLevel.MILD
    if excess < 6:
        return HeatStressLevel.MODERATE
    if excess < 10:
        return HeatStressLevel.SEVERE
    return HeatStressLevel.EXTREME


def _overall_level(levels: Sequence[HeatStressLevel]) -> HeatStressLevel:
    order = [
        HeatStressLevel.NONE,
        HeatStressLevel.MILD,
        HeatStressLevel.MODERATE,
        HeatStressLevel.SEVERE,
        HeatStressLevel.EXTREME,
    ]
    if not levels:
        return HeatStressLevel.NONE
    return max(levels, key=lambda l: order.index(l))


def _thi(temp_c: float, humidity_pct: float) -> float:
    """Livestock Temperature-Humidity Index (NRC formula)."""
    return (1.8 * temp_c + 32) - (0.55 - 0.0055 * humidity_pct) * (
        (1.8 * temp_c + 32) - 58
    )


def _thi_level(thi: float) -> HeatStressLevel:
    if thi < 72:
        return HeatStressLevel.NONE
    if thi < 80:
        return HeatStressLevel.MILD
    if thi < 90:
        return HeatStressLevel.MODERATE
    if thi < 98:
        return HeatStressLevel.SEVERE
    return HeatStressLevel.EXTREME


class HeatStressAssessor:
    """Assesses heat stress risk from weather forecasts.

    Parameters
    ----------
    crops:
        List of crops to evaluate (default: all supported crops).
    include_livestock:
        Whether to compute THI for livestock.
    """

    def __init__(
        self,
        crops: list[str] | None = None,
        *,
        include_livestock: bool = True,
    ) -> None:
        self._crops = [c.lower() for c in (crops or list(_CROP_THRESHOLDS))]
        self._include_livestock = include_livestock

    def assess(self, daily_forecasts: Sequence[DailyForecast]) -> HeatStressReport:
        if not daily_forecasts:
            return HeatStressReport(
                level=HeatStressLevel.NONE,
                max_temp_c=0.0,
                avg_temp_c=0.0,
                stress_days=0,
                total_days=0,
                affected_crops=[],
                livestock_thi=None,
                recommendations=[],
            )

        max_temp = max(d.temp_max_c for d in daily_forecasts)
        avg_temp = sum(d.temp_mean_c for d in daily_forecasts) / len(daily_forecasts)

        # Per-crop stress
        affected_crops: list[str] = []
        day_levels: list[HeatStressLevel] = []
        stress_days = 0

        for crop in self._crops:
            threshold = _CROP_THRESHOLDS.get(crop, 35.0)
            crop_stressed = any(d.temp_max_c > threshold for d in daily_forecasts)
            if crop_stressed:
                affected_crops.append(crop)

        for day in daily_forecasts:
            per_day = [
                _stress_level(day.temp_max_c, _CROP_THRESHOLDS.get(c, 35.0))
                for c in self._crops
            ]
            worst = _overall_level(per_day)
            day_levels.append(worst)
            if worst != HeatStressLevel.NONE:
                stress_days += 1

        overall = _overall_level(day_levels)

        # Livestock THI using forecast peak
        livestock_thi: LivestockTHI | None = None
        if self._include_livestock:
            # Use max day's average humidity
            max_day = max(daily_forecasts, key=lambda d: d.temp_max_c)
            avg_rh = self._avg_humidity(max_day)
            thi_val = _thi(max_day.temp_max_c, avg_rh)
            thi_lv = _thi_level(thi_val)
            affected = []
            if thi_val >= 72:
                affected.extend(["dairy cattle", "poultry"])
            if thi_val >= 80:
                affected.append("buffaloes")
            livestock_thi = LivestockTHI(
                value=round(thi_val, 1),
                level=thi_lv,
                affected_animals=affected,
                recommendation=self._livestock_rec(thi_lv),
            )

        recommendations = self._build_recs(overall, affected_crops, max_temp)

        return HeatStressReport(
            level=overall,
            max_temp_c=max_temp,
            avg_temp_c=round(avg_temp, 1),
            stress_days=stress_days,
            total_days=len(daily_forecasts),
            affected_crops=affected_crops,
            livestock_thi=livestock_thi,
            recommendations=recommendations,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _avg_humidity(day: DailyForecast) -> float:
        if day.hourly:
            return sum(h.humidity_pct for h in day.hourly) / len(day.hourly)
        return 60.0

    @staticmethod
    def _livestock_rec(level: HeatStressLevel) -> str:
        recs = {
            HeatStressLevel.NONE: "Normal husbandry practices.",
            HeatStressLevel.MILD: "Ensure shade and clean drinking water are available.",
            HeatStressLevel.MODERATE: "Increase water availability; reduce feeding during peak heat; provide fans.",
            HeatStressLevel.SEVERE: "Emergency cooling measures; restrict movement during 10 AM–4 PM; consult vet.",
            HeatStressLevel.EXTREME: "Critical: move animals to cool shelter immediately; monitor for heat stroke.",
        }
        return recs.get(level, "")

    @staticmethod
    def _build_recs(
        level: HeatStressLevel,
        crops: list[str],
        max_temp: float,
    ) -> list[str]:
        recs: list[str] = []
        if level == HeatStressLevel.NONE:
            return ["Conditions are within safe range for all crops."]

        if crops:
            recs.append(
                f"Heat stress risk for: {', '.join(crops)}. "
                "Consider irrigation scheduling to cool the root zone."
            )
        if max_temp > 40:
            recs.append(
                "Extreme heat expected. Apply reflective mulch; "
                "avoid transplanting or sowing operations."
            )
        elif max_temp > 35:
            recs.append("Irrigate during early morning or late evening to reduce heat load.")

        if "wheat" in crops:
            recs.append(
                "Wheat: high temperature at grain filling reduces yield. "
                "Apply foliar potassium or silica to improve tolerance."
            )
        if "potato" in crops or "tomato" in crops:
            recs.append(
                "Solanaceous crops: flowering/fruit set affected above 35°C. "
                "Use shade nets during hottest part of the day."
            )
        return recs
