"""Weather forecast service backed by Open-Meteo (free, no key required).

Fetches current conditions and multi-day forecasts, normalises the raw
API response into typed Pydantic models, and applies two-level caching.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import date, datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from .cache import WeatherCache
from .client import WeatherClient, WeatherClientError
from .location import LocationResolver, WeatherLocation
from .models import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    WeatherCondition,
    WeatherForecast,
    condition_from_wmo,
)

__all__ = [
    "ForecastRequest",
    "ForecastService",
    "ForecastServiceError",
]

logger = logging.getLogger(__name__)

# Open-Meteo variables requested for hourly data
_HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "precipitation_probability",
    "weathercode",
    "windspeed_10m",
    "winddirection_10m",
    "cloudcover",
    "uv_index",
    "dewpoint_2m",
    "soil_temperature_0cm",
    "soil_moisture_0_to_1cm",
    "et0_fao_evapotranspiration",
]

_DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "windspeed_10m_max",
    "windgusts_10m_max",
    "winddirection_10m_dominant",
    "weathercode",
    "uv_index_max",
    "sunrise",
    "sunset",
    "sunshine_duration",
    "et0_fao_evapotranspiration",
]

_CURRENT_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "weathercode",
    "windspeed_10m",
    "winddirection_10m",
    "cloudcover",
    "surface_pressure",
]


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------


class ForecastRequest(BaseModel):
    """Parameters for a forecast fetch."""

    location: WeatherLocation
    days: int = Field(default=7, ge=1, le=16, description="Number of forecast days.")
    include_hourly: bool = Field(default=True)
    include_current: bool = Field(default=True)
    timezone: str = Field(default="auto")

    model_config = {"frozen": True}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ForecastServiceError(Exception):
    """Raised on unrecoverable forecast fetch errors."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class ForecastService:
    """Fetches and caches weather forecasts from Open-Meteo.

    Parameters
    ----------
    client:
        Shared :class:`~krishimitra_weather.client.WeatherClient`.
    cache:
        Optional :class:`~krishimitra_weather.cache.WeatherCache`.
    resolver:
        Optional :class:`~krishimitra_weather.location.LocationResolver`
        for string-based location queries.
    """

    def __init__(
        self,
        client: WeatherClient,
        cache: WeatherCache | None = None,
        resolver: LocationResolver | None = None,
    ) -> None:
        self._client = client
        self._cache = cache
        self._resolver = resolver

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_forecast(self, request: ForecastRequest) -> WeatherForecast:
        """Fetch forecast for the given :class:`ForecastRequest`.

        Returns cached data when available.
        """
        cache_key = self._cache_key(request)

        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.debug("Forecast cache hit: %s", cache_key)
                try:
                    return WeatherForecast.model_validate(cached)
                except Exception:
                    pass  # stale/invalid → re-fetch

        forecast = await self._fetch(request)

        if self._cache:
            await self._cache.set(
                cache_key,
                forecast.model_dump(mode="json"),
                ttl=1800,
            )

        return forecast

    async def get_forecast_for_query(
        self,
        query: str,
        days: int = 7,
        *,
        include_hourly: bool = True,
    ) -> WeatherForecast:
        """Resolve *query* string to a location then fetch a forecast."""
        if self._resolver is None:
            raise ForecastServiceError(
                "LocationResolver not configured; pass a WeatherLocation directly."
            )
        location = await self._resolver.resolve(query)
        request = ForecastRequest(
            location=location,
            days=days,
            include_hourly=include_hourly,
        )
        return await self.get_forecast(request)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _fetch(self, request: ForecastRequest) -> WeatherForecast:
        loc = request.location
        params: dict[str, Any] = {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "forecast_days": request.days,
            "daily": ",".join(_DAILY_VARS),
            "timezone": request.timezone,
            "windspeed_unit": "kmh",
        }

        if request.include_current:
            params["current"] = ",".join(_CURRENT_VARS)

        if request.include_hourly:
            params["hourly"] = ",".join(_HOURLY_VARS)

        try:
            data = await self._client.open_meteo("forecast", params)
        except WeatherClientError as exc:
            raise ForecastServiceError(
                f"Failed to fetch forecast for {loc.name}: {exc}"
            ) from exc

        return self._parse(data, loc)

    def _parse(self, data: dict[str, Any], location: WeatherLocation) -> WeatherForecast:
        daily_list = self._parse_daily(data)
        hourly_by_date = self._parse_hourly(data)

        # Attach hourly slices to their day
        for day in daily_list:
            day.hourly = hourly_by_date.get(day.date, [])

        current = self._parse_current(data)

        return WeatherForecast(
            location=location,
            current=current,
            daily=daily_list,
        )

    def _parse_current(self, data: dict[str, Any]) -> CurrentWeather | None:
        cur = data.get("current")
        if not cur:
            return None
        vars_ = cur.get("current_units", {})
        ts_raw = cur.get("time")
        try:
            ts = datetime.fromisoformat(ts_raw).replace(tzinfo=timezone.utc)
        except Exception:
            ts = datetime.now(tz=timezone.utc)

        wmo = cur.get("weathercode", 0)
        return CurrentWeather(
            timestamp=ts,
            temperature_c=float(cur.get("temperature_2m", 0)),
            feels_like_c=_opt_float(cur.get("apparent_temperature")),
            humidity_pct=float(cur.get("relative_humidity_2m", 0)),
            wind_speed_kmh=float(cur.get("windspeed_10m", 0)),
            wind_direction_deg=_opt_float(cur.get("winddirection_10m")),
            precipitation_mm=float(cur.get("precipitation", 0)),
            cloud_cover_pct=float(cur.get("cloudcover", 0)),
            condition=condition_from_wmo(int(wmo)),
            pressure_hpa=_opt_float(cur.get("surface_pressure")),
        )

    def _parse_daily(self, data: dict[str, Any]) -> list[DailyForecast]:
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        results: list[DailyForecast] = []

        for i, d in enumerate(dates):
            wmo = _idx(daily, "weathercode", i, 0)
            sunrise_raw = _idx(daily, "sunrise", i, None)
            sunset_raw = _idx(daily, "sunset", i, None)

            sunshine_s = _opt_float(_idx(daily, "sunshine_duration", i, None))
            sunshine_h = sunshine_s / 3600 if sunshine_s is not None else None

            results.append(
                DailyForecast(
                    date=date.fromisoformat(d),
                    temp_max_c=float(_idx(daily, "temperature_2m_max", i, 0)),
                    temp_min_c=float(_idx(daily, "temperature_2m_min", i, 0)),
                    precipitation_mm=float(_idx(daily, "precipitation_sum", i, 0)),
                    precipitation_probability_pct=float(
                        _idx(daily, "precipitation_probability_max", i, 0)
                    ),
                    wind_speed_max_kmh=float(_idx(daily, "windspeed_10m_max", i, 0)),
                    wind_gusts_max_kmh=_opt_float(
                        _idx(daily, "windgusts_10m_max", i, None)
                    ),
                    wind_direction_dominant_deg=_opt_float(
                        _idx(daily, "winddirection_10m_dominant", i, None)
                    ),
                    condition=condition_from_wmo(int(wmo or 0)),
                    uv_index_max=_opt_float(_idx(daily, "uv_index_max", i, None)),
                    sunrise=_parse_dt(sunrise_raw),
                    sunset=_parse_dt(sunset_raw),
                    sunshine_duration_h=sunshine_h,
                    et0_mm=_opt_float(
                        _idx(daily, "et0_fao_evapotranspiration", i, None)
                    ),
                )
            )

        return results

    def _parse_hourly(
        self, data: dict[str, Any]
    ) -> dict[date, list[HourlyForecast]]:
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        by_date: dict[date, list[HourlyForecast]] = {}

        for i, t in enumerate(times):
            try:
                ts = datetime.fromisoformat(t)
            except Exception:
                continue
            wmo = _idx(hourly, "weathercode", i, 0)
            hf = HourlyForecast(
                timestamp=ts,
                temperature_c=float(_idx(hourly, "temperature_2m", i, 0)),
                humidity_pct=float(_idx(hourly, "relative_humidity_2m", i, 0)),
                precipitation_mm=float(_idx(hourly, "precipitation", i, 0)),
                precipitation_probability_pct=float(
                    _idx(hourly, "precipitation_probability", i, 0)
                ),
                wind_speed_kmh=float(_idx(hourly, "windspeed_10m", i, 0)),
                wind_direction_deg=_opt_float(_idx(hourly, "winddirection_10m", i, None)),
                cloud_cover_pct=float(_idx(hourly, "cloudcover", i, 0)),
                condition=condition_from_wmo(int(wmo or 0)),
                uv_index=_opt_float(_idx(hourly, "uv_index", i, None)),
                dew_point_c=_opt_float(_idx(hourly, "dewpoint_2m", i, None)),
                soil_temperature_c=_opt_float(
                    _idx(hourly, "soil_temperature_0cm", i, None)
                ),
                soil_moisture=_opt_float(
                    _idx(hourly, "soil_moisture_0_to_1cm", i, None)
                ),
                evapotranspiration_mm=_opt_float(
                    _idx(hourly, "et0_fao_evapotranspiration", i, None)
                ),
            )
            day = ts.date()
            by_date.setdefault(day, []).append(hf)

        return by_date

    # ------------------------------------------------------------------
    # Cache key
    # ------------------------------------------------------------------

    @staticmethod
    def _cache_key(request: ForecastRequest) -> str:
        loc = request.location
        raw = (
            f"{loc.latitude:.3f}:{loc.longitude:.3f}:"
            f"{request.days}:{request.include_hourly}"
        )
        return "forecast:" + hashlib.md5(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _idx(d: dict[str, Any], key: str, i: int, default: Any) -> Any:
    lst = d.get(key)
    if lst and i < len(lst) and lst[i] is not None:
        return lst[i]
    return default


def _opt_float(val: Any) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _parse_dt(raw: Any) -> datetime | None:
    if raw is None:
        return None
    try:
        return datetime.fromisoformat(str(raw))
    except Exception:
        return None
