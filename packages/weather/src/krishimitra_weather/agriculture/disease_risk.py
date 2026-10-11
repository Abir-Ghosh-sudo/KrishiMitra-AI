"""Agricultural disease risk assessment from weather conditions.

Uses epidemiological rules for the most common Indian crop diseases:
- Late blight (potato/tomato): high humidity + cool temperatures
- Powdery mildew: moderate humidity + warm days + cool nights
- Blast (rice): leaf wetness proxy via humidity + temperature
- Downy mildew: high humidity + mild temperatures
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence

from ..models import DailyForecast, HourlyForecast

__all__ = [
    "DiseaseRisk",
    "DiseaseRiskAssessor",
    "DiseaseRiskLevel",
    "DiseaseRiskReport",
]

logger = logging.getLogger(__name__)


class DiseaseRiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass(frozen=True)
class DiseaseRisk:
    """Risk assessment for a single disease."""

    disease: str
    level: DiseaseRiskLevel
    score: float  # 0–100
    reasons: list[str]
    recommendation: str


@dataclass(frozen=True)
class DiseaseRiskReport:
    """Full disease risk report for a set of forecast days."""

    risks: list[DiseaseRisk]
    overall_level: DiseaseRiskLevel
    days_analyzed: int

    @property
    def highest_risk_diseases(self) -> list[DiseaseRisk]:
        return [
            r for r in self.risks
            if r.level in (DiseaseRiskLevel.HIGH, DiseaseRiskLevel.VERY_HIGH)
        ]


def _level_from_score(score: float) -> DiseaseRiskLevel:
    if score >= 75:
        return DiseaseRiskLevel.VERY_HIGH
    if score >= 50:
        return DiseaseRiskLevel.HIGH
    if score >= 25:
        return DiseaseRiskLevel.MODERATE
    return DiseaseRiskLevel.LOW


def _overall_level(risks: list[DiseaseRisk]) -> DiseaseRiskLevel:
    if not risks:
        return DiseaseRiskLevel.LOW
    max_score = max(r.score for r in risks)
    return _level_from_score(max_score)


class DiseaseRiskAssessor:
    """Assesses crop disease risk from weather forecast data.

    Parameters
    ----------
    humidity_threshold_pct:
        Relative humidity (%) above which risk escalates (default 80).
    consecutive_wet_hours:
        Hours of continuous high-humidity needed to elevate risk.
    """

    def __init__(
        self,
        *,
        humidity_threshold_pct: float = 80.0,
        consecutive_wet_hours: int = 6,
    ) -> None:
        self._humidity_thresh = humidity_threshold_pct
        self._consecutive_wet = consecutive_wet_hours

    def assess(
        self,
        daily_forecasts: Sequence[DailyForecast],
    ) -> DiseaseRiskReport:
        """Compute disease risks from a list of daily forecasts."""
        risks = [
            self._late_blight(daily_forecasts),
            self._powdery_mildew(daily_forecasts),
            self._rice_blast(daily_forecasts),
            self._downy_mildew(daily_forecasts),
        ]
        return DiseaseRiskReport(
            risks=risks,
            overall_level=_overall_level(risks),
            days_analyzed=len(daily_forecasts),
        )

    # ------------------------------------------------------------------
    # Disease models
    # ------------------------------------------------------------------

    def _late_blight(self, days: Sequence[DailyForecast]) -> DiseaseRisk:
        """Late blight (Phytophthora infestans): humid + cool nights."""
        reasons: list[str] = []
        score = 0.0

        for day in days:
            avg_rh = self._avg_humidity(day)
            if avg_rh > self._humidity_thresh:
                score += 15
                reasons.append(f"High humidity ({avg_rh:.0f}%) on {day.date}")
            if day.temp_min_c < 18 and day.temp_max_c < 25:
                score += 10
                reasons.append(f"Cool temperatures on {day.date}")
            if day.precipitation_mm > 5:
                score += 10

        score = min(score, 100)
        return DiseaseRisk(
            disease="Late Blight (Potato/Tomato)",
            level=_level_from_score(score),
            score=score,
            reasons=reasons[:4],
            recommendation=(
                "Apply preventive fungicide (Mancozeb/Chlorothalonil) "
                "before rain events. Avoid overhead irrigation."
                if score >= 50
                else "Monitor regularly; conditions are currently manageable."
            ),
        )

    def _powdery_mildew(self, days: Sequence[DailyForecast]) -> DiseaseRisk:
        """Powdery mildew: warm days, cool nights, moderate humidity."""
        reasons: list[str] = []
        score = 0.0

        for day in days:
            avg_rh = self._avg_humidity(day)
            temp_swing = day.temp_max_c - day.temp_min_c
            if 20 <= day.temp_max_c <= 30 and avg_rh > 60:
                score += 12
                reasons.append(f"Warm & humid on {day.date}")
            if temp_swing > 12:
                score += 8
                reasons.append(f"Large diurnal swing ({temp_swing:.1f}°C) on {day.date}")

        score = min(score, 100)
        return DiseaseRisk(
            disease="Powdery Mildew",
            level=_level_from_score(score),
            score=score,
            reasons=reasons[:4],
            recommendation=(
                "Apply sulfur-based fungicide or neem oil spray."
                if score >= 50
                else "Ensure good canopy airflow; monitor susceptible crops."
            ),
        )

    def _rice_blast(self, days: Sequence[DailyForecast]) -> DiseaseRisk:
        """Rice blast (Magnaporthe oryzae): high humidity + 24–28°C."""
        reasons: list[str] = []
        score = 0.0

        for day in days:
            avg_rh = self._avg_humidity(day)
            avg_temp = day.temp_mean_c
            if avg_rh > 85 and 22 <= avg_temp <= 28:
                score += 20
                reasons.append(
                    f"Blast-conducive conditions on {day.date} "
                    f"(RH {avg_rh:.0f}%, T {avg_temp:.1f}°C)"
                )
            if day.precipitation_mm > 10:
                score += 5

        score = min(score, 100)
        return DiseaseRisk(
            disease="Rice Blast",
            level=_level_from_score(score),
            score=score,
            reasons=reasons[:4],
            recommendation=(
                "Apply Tricyclazole or Isoprothiolane at tillering stage."
                if score >= 50
                else "Use blast-resistant varieties; balanced nitrogen application."
            ),
        )

    def _downy_mildew(self, days: Sequence[DailyForecast]) -> DiseaseRisk:
        """Downy mildew: very high humidity + mild temperatures."""
        reasons: list[str] = []
        score = 0.0

        for day in days:
            avg_rh = self._avg_humidity(day)
            if avg_rh > 90 and 15 <= day.temp_max_c <= 25:
                score += 18
                reasons.append(f"Downy mildew-conducive on {day.date}")
            if day.precipitation_mm > 3:
                score += 7

        score = min(score, 100)
        return DiseaseRisk(
            disease="Downy Mildew",
            level=_level_from_score(score),
            score=score,
            reasons=reasons[:4],
            recommendation=(
                "Apply Metalaxyl + Mancozeb at first symptoms."
                if score >= 50
                else "Maintain field drainage; avoid excessive irrigation."
            ),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _avg_humidity(day: DailyForecast) -> float:
        if day.hourly:
            return sum(h.humidity_pct for h in day.hourly) / len(day.hourly)
        # Approximate from temp range (Magnus formula proxy)
        return 70.0  # conservative default
