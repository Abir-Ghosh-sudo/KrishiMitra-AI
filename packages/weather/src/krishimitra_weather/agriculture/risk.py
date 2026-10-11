"""Agricultural weather risk service — unified facade over all risk modules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence

from ..models import DailyForecast, WeatherForecast
from .disease_risk import DiseaseRiskAssessor, DiseaseRiskReport
from .heat_stress import HeatStressAssessor, HeatStressReport
from .irrigation_window import IrrigationRecommendation, IrrigationWindowFinder
from .pest_risk import PestRiskAssessor, PestRiskReport
from .rain_risk import RainRiskAssessor, RainRiskReport
from .spray_window import SprayWindowFinder, SprayWindowReport

__all__ = [
    "AgriculturalRiskReport",
    "AgriculturalWeatherRisk",
    "WeatherRiskLevel",
    "WeatherRiskService",
]


class WeatherRiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AgriculturalWeatherRisk:
    """Aggregated agricultural weather risk summary."""

    overall_level: WeatherRiskLevel
    disease: DiseaseRiskReport
    heat_stress: HeatStressReport
    pest: PestRiskReport
    rain: RainRiskReport
    irrigation: IrrigationRecommendation
    spray: SprayWindowReport
    top_actions: list[str]


# Alias for __init__.py compatibility
AgriculturalRiskReport = AgriculturalWeatherRisk

_LEVEL_ORDER = [
    WeatherRiskLevel.LOW,
    WeatherRiskLevel.MODERATE,
    WeatherRiskLevel.HIGH,
    WeatherRiskLevel.CRITICAL,
]


def _to_weather_risk(level_str: str) -> WeatherRiskLevel:
    mapping = {
        "low": WeatherRiskLevel.LOW,
        "moderate": WeatherRiskLevel.MODERATE,
        "high": WeatherRiskLevel.HIGH,
        "very_high": WeatherRiskLevel.CRITICAL,
        "severe": WeatherRiskLevel.HIGH,
        "extreme": WeatherRiskLevel.CRITICAL,
        "none": WeatherRiskLevel.LOW,
        "mild": WeatherRiskLevel.LOW,
    }
    return mapping.get(level_str.lower(), WeatherRiskLevel.LOW)


def _max_level(*levels: WeatherRiskLevel) -> WeatherRiskLevel:
    return max(levels, key=lambda l: _LEVEL_ORDER.index(l))


class WeatherRiskService:
    """Unified service that computes all agricultural weather risks.

    Parameters
    ----------
    crops:
        List of crops grown (influences heat stress and disease checks).
    include_livestock:
        Whether to include livestock THI in heat stress assessment.
    """

    def __init__(
        self,
        crops: list[str] | None = None,
        *,
        include_livestock: bool = True,
    ) -> None:
        self._disease = DiseaseRiskAssessor()
        self._heat = HeatStressAssessor(crops=crops, include_livestock=include_livestock)
        self._pest = PestRiskAssessor()
        self._rain = RainRiskAssessor()
        self._irrigation = IrrigationWindowFinder()
        self._spray = SprayWindowFinder()

    def assess(self, forecast: WeatherForecast) -> AgriculturalWeatherRisk:
        """Run all risk assessors against *forecast* and return a unified report."""
        days = forecast.daily

        disease_report = self._disease.assess(days)
        heat_report = self._heat.assess(days)
        pest_report = self._pest.assess(days)
        rain_report = self._rain.assess(days)
        irrigation_report = self._irrigation.find(days)
        spray_report = self._spray.find(days)

        # Compute overall risk level
        risk_levels = [
            _to_weather_risk(disease_report.overall_level),
            _to_weather_risk(heat_report.level),
            _to_weather_risk(pest_report.overall_level),
        ]
        if rain_report.flood_alert:
            risk_levels.append(WeatherRiskLevel.CRITICAL)
        elif rain_report.waterlogging_risk:
            risk_levels.append(WeatherRiskLevel.HIGH)

        overall = _max_level(*risk_levels)

        top_actions = self._compile_actions(
            disease_report,
            heat_report,
            pest_report,
            rain_report,
            irrigation_report,
            spray_report,
        )

        return AgriculturalWeatherRisk(
            overall_level=overall,
            disease=disease_report,
            heat_stress=heat_report,
            pest=pest_report,
            rain=rain_report,
            irrigation=irrigation_report,
            spray=spray_report,
            top_actions=top_actions,
        )

    @staticmethod
    def _compile_actions(
        disease: DiseaseRiskReport,
        heat: HeatStressReport,
        pest: PestRiskReport,
        rain: RainRiskReport,
        irrigation: IrrigationRecommendation,
        spray: SprayWindowReport,
    ) -> list[str]:
        actions: list[str] = []

        if rain.flood_alert:
            actions.append("⚠️ FLOOD ALERT: protect crops and move equipment to high ground.")
        elif rain.waterlogging_risk:
            actions.append("Clear drainage channels before expected heavy rains.")

        for risk in disease.highest_risk_diseases:
            actions.append(f"Disease: {risk.recommendation}")

        for risk in pest.high_risk_pests:
            actions.append(f"Pest ({risk.pest}): {risk.recommendation}")

        if heat.level not in ("none", "mild"):
            for rec in heat.recommendations[:2]:
                actions.append(f"Heat: {rec}")

        if not irrigation.skip_irrigation and irrigation.net_irrigation_need_mm > 0:
            actions.append(
                f"Irrigate {irrigation.net_irrigation_need_mm:.0f} mm — "
                f"use optimal windows: {', '.join(str(w.start.strftime('%d %b %I %p')) for w in irrigation.best_windows[:2]) or 'early morning'}."
            )

        if spray.best_day:
            actions.append(
                f"Best spray day: {spray.best_day} — "
                f"{spray.total_suitable_hours} suitable hour(s) available."
            )

        return actions[:8]  # cap to top 8 for readability
