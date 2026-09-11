"""Weather models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WeatherObservation(BaseModel):
    """Current or historical weather observation."""

    model_config = ConfigDict(extra="forbid")

    observed_at: datetime

    temperature_c: float | None = None
    feels_like_c: float | None = None

    relative_humidity_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    precipitation_mm: float | None = Field(
        default=None,
        ge=0.0,
    )

    wind_speed_kmh: float | None = Field(
        default=None,
        ge=0.0,
    )

    wind_direction_degrees: float | None = Field(
        default=None,
        ge=0.0,
        le=360.0,
    )

    solar_radiation_w_m2: float | None = Field(
        default=None,
        ge=0.0,
    )


class WeatherForecast(BaseModel):
    """Forecast weather conditions for a future period."""

    model_config = ConfigDict(extra="forbid")

    forecast_time: datetime

    temperature_c: float | None = None

    precipitation_probability_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    precipitation_mm: float | None = Field(
        default=None,
        ge=0.0,
    )

    relative_humidity_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    wind_speed_kmh: float | None = Field(
        default=None,
        ge=0.0,
    )


class WeatherRisk(BaseModel):
    """Derived agricultural weather risk."""

    model_config = ConfigDict(extra="forbid")

    rain_risk: float = Field(ge=0.0, le=1.0)
    heat_stress_risk: float = Field(ge=0.0, le=1.0)
    fungal_risk: float = Field(ge=0.0, le=1.0)
    spray_risk: float = Field(ge=0.0, le=1.0)


__all__ = [
    "WeatherForecast",
    "WeatherObservation",
    "WeatherRisk",
]