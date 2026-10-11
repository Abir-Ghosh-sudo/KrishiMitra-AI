"""Pest activity risk assessment from weather forecasts.

Models weather-driven pest pressure for key Indian agricultural pests.
Higher temperatures and specific humidity windows accelerate pest cycles.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence

from ..models import DailyForecast

__all__ = [
    "PestRisk",
    "PestRiskAssessor",
    "PestRiskLevel",
    "PestRiskReport",
]

logger = logging.getLogger(__name__)


class PestRiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass(frozen=True)
class PestRisk:
    """Risk assessment for a single pest."""

    pest: str
    level: PestRiskLevel
    score: float  # 0–100
    activity_driver: str
    recommendation: str


@dataclass(frozen=True)
class PestRiskReport:
    """Aggregated pest risk report."""

    risks: list[PestRisk]
    overall_level: PestRiskLevel
    days_analyzed: int

    @property
    def high_risk_pests(self) -> list[PestRisk]:
        return [
            r for r in self.risks
            if r.level in (PestRiskLevel.HIGH, PestRiskLevel.VERY_HIGH)
        ]


def _level_from_score(score: float) -> PestRiskLevel:
    if score >= 75:
        return PestRiskLevel.VERY_HIGH
    if score >= 50:
        return PestRiskLevel.HIGH
    if score >= 25:
        return PestRiskLevel.MODERATE
    return PestRiskLevel.LOW


def _overall_level(risks: list[PestRisk]) -> PestRiskLevel:
    if not risks:
        return PestRiskLevel.LOW
    order = [PestRiskLevel.LOW, PestRiskLevel.MODERATE, PestRiskLevel.HIGH, PestRiskLevel.VERY_HIGH]
    return max(risks, key=lambda r: order.index(r.level)).level


class PestRiskAssessor:
    """Computes weather-driven pest risk from daily forecast data."""

    def assess(self, daily_forecasts: Sequence[DailyForecast]) -> PestRiskReport:
        risks = [
            self._aphid_risk(daily_forecasts),
            self._whitefly_risk(daily_forecasts),
            self._armyworm_risk(daily_forecasts),
            self._locust_risk(daily_forecasts),
            self._thrips_risk(daily_forecasts),
        ]
        return PestRiskReport(
            risks=risks,
            overall_level=_overall_level(risks),
            days_analyzed=len(daily_forecasts),
        )

    # ------------------------------------------------------------------
    # Pest models
    # ------------------------------------------------------------------

    def _aphid_risk(self, days: Sequence[DailyForecast]) -> PestRisk:
        """Aphids thrive in 18–24°C with moderate humidity; rain suppresses."""
        score = 0.0
        for day in days:
            avg_rh = _avg_rh(day)
            if 16 <= day.temp_mean_c <= 26 and 50 <= avg_rh <= 75:
                score += 15
            if day.precipitation_mm > 10:  # heavy rain knocks aphids off
                score -= 10
        score = max(0.0, min(score, 100))
        return PestRisk(
            pest="Aphids",
            level=_level_from_score(score),
            score=score,
            activity_driver="Warm, moderately humid conditions favour rapid multiplication.",
            recommendation=(
                "Apply neem oil spray or insecticidal soap. Conserve natural enemies."
                if score >= 50
                else "Scout weekly; beneficial insects like ladybirds typically control aphid populations."
            ),
        )

    def _whitefly_risk(self, days: Sequence[DailyForecast]) -> PestRisk:
        """Whitefly: hot and dry (25–35°C, low humidity)."""
        score = 0.0
        for day in days:
            avg_rh = _avg_rh(day)
            if 25 <= day.temp_max_c <= 38 and avg_rh < 60:
                score += 15
            if day.temp_max_c > 40:
                score -= 5  # extreme heat also suppresses
        score = max(0.0, min(score, 100))
        return PestRisk(
            pest="Whitefly",
            level=_level_from_score(score),
            score=score,
            activity_driver="Hot, dry weather accelerates whitefly life cycle.",
            recommendation=(
                "Use yellow sticky traps; apply buprofezin or spiromesifen. "
                "Manage vector-borne viruses (TYLCV in tomato)."
                if score >= 50
                else "Monitor undersides of leaves; maintain adequate soil moisture."
            ),
        )

    def _armyworm_risk(self, days: Sequence[DailyForecast]) -> PestRisk:
        """Fall Armyworm (FAW): warm, humid; eggs hatch in 25–30°C."""
        score = 0.0
        for day in days:
            avg_rh = _avg_rh(day)
            if 22 <= day.temp_mean_c <= 30 and avg_rh > 60:
                score += 12
            if day.precipitation_mm > 5:
                score += 5  # moist soil favours pupation
        score = min(score, 100)
        return PestRisk(
            pest="Fall Armyworm (FAW)",
            level=_level_from_score(score),
            score=score,
            activity_driver="Warm humid nights favour moth flight and oviposition.",
            recommendation=(
                "Apply emamectin benzoate or chlorantraniliprole at early instar. "
                "Use pheromone traps for adult monitoring."
                if score >= 50
                else "Scout maize/sorghum whorls for frass; early action is critical."
            ),
        )

    def _locust_risk(self, days: Sequence[DailyForecast]) -> PestRisk:
        """Desert locust: warm (25–35°C) + recent rainfall enabling vegetation."""
        score = 0.0
        warm_days = sum(1 for d in days if 25 <= d.temp_max_c <= 38)
        rain_days = sum(1 for d in days if d.precipitation_mm > 2)
        if warm_days > len(days) * 0.5:
            score += 30
        if rain_days > 0:
            score += 20 * (rain_days / len(days)) if days else 0
        score = min(score, 100)
        return PestRisk(
            pest="Desert Locust",
            level=_level_from_score(score),
            score=score,
            activity_driver="Warm conditions + greening after rain support locust breeding.",
            recommendation=(
                "Report sightings to state agriculture department immediately. "
                "Spray malathion ULV or chlorpyrifos as directed."
                if score >= 50
                else "Monitor border areas and sandy soils; check NCPOR advisories."
            ),
        )

    def _thrips_risk(self, days: Sequence[DailyForecast]) -> PestRisk:
        """Thrips: hot and dry (above 30°C, low RH)."""
        score = 0.0
        for day in days:
            avg_rh = _avg_rh(day)
            if day.temp_max_c > 30 and avg_rh < 50:
                score += 18
        score = min(score, 100)
        return PestRisk(
            pest="Thrips",
            level=_level_from_score(score),
            score=score,
            activity_driver="Hot, dry conditions cause rapid thrips population build-up.",
            recommendation=(
                "Apply spinosad or imidacloprid. Use blue sticky traps. "
                "TSWV transmission risk increases — remove infected plants."
                if score >= 50
                else "Maintain canopy humidity; conserve predatory mites."
            ),
        )


def _avg_rh(day: DailyForecast) -> float:
    if day.hourly:
        return sum(h.humidity_pct for h in day.hourly) / len(day.hourly)
    return 65.0  # neutral default
