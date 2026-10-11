"""Shared Pydantic models for weather data representations."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

__all__ = [
    "CurrentWeather",
    "DailyForecast",
    "HourlyForecast",
    "WeatherCondition",
    "WeatherForecast",
    "WeatherLocation",
]

# Re-export WeatherLocation from location module so __init__.py can import from .models
from .location import WeatherLocation  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class WeatherCondition(StrEnum):
    """WMO Weather Interpretation Code → descriptive category."""

    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    OVERCAST = "overcast"
    FOG = "fog"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    UNKNOWN = "unknown"


# WMO code → WeatherCondition mapping (Open-Meteo uses WMO codes)
_WMO_MAP: dict[int, WeatherCondition] = {
    0: WeatherCondition.CLEAR,
    1: WeatherCondition.CLEAR,
    2: WeatherCondition.PARTLY_CLOUDY,
    3: WeatherCondition.OVERCAST,
    45: WeatherCondition.FOG,
    48: WeatherCondition.FOG,
    51: WeatherCondition.DRIZZLE,
    53: WeatherCondition.DRIZZLE,
    55: WeatherCondition.DRIZZLE,
    61: WeatherCondition.RAIN,
    63: WeatherCondition.RAIN,
    65: WeatherCondition.HEAVY_RAIN,
    80: WeatherCondition.RAIN,
    81: WeatherCondition.RAIN,
    82: WeatherCondition.HEAVY_RAIN,
    95: WeatherCondition.THUNDERSTORM,
    96: WeatherCondition.THUNDERSTORM,
    99: WeatherCondition.THUNDERSTORM,
    71: WeatherCondition.SNOW,
    73: WeatherCondition.SNOW,
    75: WeatherCondition.SNOW,
    77: WeatherCondition.SNOW,
    85: WeatherCondition.SNOW,
    86: WeatherCondition.SNOW,
}


def condition_from_wmo(code: int) -> WeatherCondition:
    """Map a WMO weather code to a :class:`WeatherCondition`."""
    return _WMO_MAP.get(code, WeatherCondition.UNKNOWN)


# ---------------------------------------------------------------------------
# Current conditions
# ---------------------------------------------------------------------------


class CurrentWeather(BaseModel):
    """Snapshot of current weather at a location."""

    timestamp: datetime
    temperature_c: float = Field(..., description="Air temperature at 2 m (°C).")
    feels_like_c: float | None = Field(default=None)
    humidity_pct: float = Field(..., ge=0, le=100, description="Relative humidity (%).")
    wind_speed_kmh: float = Field(..., ge=0)
    wind_direction_deg: float | None = Field(default=None, ge=0, le=360)
    precipitation_mm: float = Field(default=0.0, ge=0)
    cloud_cover_pct: float = Field(default=0.0, ge=0, le=100)
    condition: WeatherCondition = WeatherCondition.UNKNOWN
    uv_index: float | None = Field(default=None, ge=0)
    pressure_hpa: float | None = Field(default=None)
    dew_point_c: float | None = Field(default=None)
    visibility_km: float | None = Field(default=None, ge=0)

    model_config = {"frozen": True}


# ---------------------------------------------------------------------------
# Hourly forecast
# ---------------------------------------------------------------------------


class HourlyForecast(BaseModel):
    """Single-hour forecast slice."""

    timestamp: datetime
    temperature_c: float
    humidity_pct: float = Field(..., ge=0, le=100)
    precipitation_mm: float = Field(default=0.0, ge=0)
    precipitation_probability_pct: float = Field(default=0.0, ge=0, le=100)
    wind_speed_kmh: float = Field(default=0.0, ge=0)
    wind_direction_deg: float | None = Field(default=None)
    cloud_cover_pct: float = Field(default=0.0, ge=0, le=100)
    condition: WeatherCondition = WeatherCondition.UNKNOWN
    uv_index: float | None = Field(default=None, ge=0)
    dew_point_c: float | None = Field(default=None)
    soil_temperature_c: float | None = Field(default=None)
    soil_moisture: float | None = Field(default=None, ge=0, le=1)
    evapotranspiration_mm: float | None = Field(default=None)

    model_config = {"frozen": True}


# ---------------------------------------------------------------------------
# Daily forecast
# ---------------------------------------------------------------------------


class DailyForecast(BaseModel):
    """Aggregated forecast for a single calendar day."""

    date: date
    temp_max_c: float
    temp_min_c: float
    precipitation_mm: float = Field(default=0.0, ge=0)
    precipitation_probability_pct: float = Field(default=0.0, ge=0, le=100)
    wind_speed_max_kmh: float = Field(default=0.0, ge=0)
    wind_gusts_max_kmh: float | None = Field(default=None)
    wind_direction_dominant_deg: float | None = Field(default=None)
    condition: WeatherCondition = WeatherCondition.UNKNOWN
    uv_index_max: float | None = Field(default=None, ge=0)
    sunrise: datetime | None = Field(default=None)
    sunset: datetime | None = Field(default=None)
    sunshine_duration_h: float | None = Field(default=None, ge=0)
    et0_mm: float | None = Field(
        default=None, description="Reference evapotranspiration (mm/day)."
    )
    hourly: list[HourlyForecast] = Field(default_factory=list)

    @property
    def temp_mean_c(self) -> float:
        return (self.temp_max_c + self.temp_min_c) / 2

    model_config = {"frozen": False}


# ---------------------------------------------------------------------------
# Full forecast bundle
# ---------------------------------------------------------------------------


class WeatherForecast(BaseModel):
    """Complete forecast response for a location."""

    location: WeatherLocation
    current: CurrentWeather | None = None
    daily: list[DailyForecast] = Field(default_factory=list)
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now().astimezone()
    )

    @property
    def today(self) -> DailyForecast | None:
        return self.daily[0] if self.daily else None

    model_config = {"frozen": False}
