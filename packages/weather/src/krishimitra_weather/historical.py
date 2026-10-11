"""Historical weather data retrieval via Open-Meteo Archive API.

Open-Meteo's /archive endpoint provides ERA5-reanalysis data from 1940
to ~5 days before today, free and without an API key.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from .cache import WeatherCache
from .client import WeatherClient, WeatherClientError
from .location import WeatherLocation
from .models import DailyForecast, HourlyForecast, condition_from_wmo

__all__ = [
    "HistoricalRequest",
    "HistoricalResponse",
    "HistoricalService",
    "HistoricalServiceError",
]

logger = logging.getLogger(__name__)

_ARCHIVE_BASE = "https://archive-api.open-meteo.com/v1"

_HIST_DAILY = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
    "weathercode",
    "et0_fao_evapotranspiration",
    "sunrise",
    "sunset",
]

_HIST_HOURLY = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "windspeed_10m",
    "weathercode",
    "soil_temperature_0cm",
    "soil_moisture_0_to_1cm",
    "et0_fao_evapotranspiration",
]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class HistoricalRequest(BaseModel):
    """Parameters for a historical weather query."""

    location: WeatherLocation
    start_date: date
    end_date: date
    include_hourly: bool = Field(default=False)
    timezone: str = Field(default="auto")

    model_config = {"frozen": True}


class HistoricalResponse(BaseModel):
    """Historical weather data for a date range."""

    location: WeatherLocation
    start_date: date
    end_date: date
    daily: list[DailyForecast] = Field(default_factory=list)
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now().astimezone()
    )

    @property
    def total_precipitation_mm(self) -> float:
        return sum(d.precipitation_mm for d in self.daily)

    @property
    def avg_temp_c(self) -> float | None:
        if not self.daily:
            return None
        return sum(d.temp_mean_c for d in self.daily) / len(self.daily)

    model_config = {"frozen": False}


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class HistoricalServiceError(Exception):
    """Raised on unrecoverable historical fetch errors."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class HistoricalService:
    """Retrieves historical weather from Open-Meteo Archive API.

    Parameters
    ----------
    client:
        :class:`~krishimitra_weather.client.WeatherClient` instance.
    cache:
        Optional two-level cache (longer TTL recommended for historical
        data since it never changes).
    """

    def __init__(
        self,
        client: WeatherClient,
        cache: WeatherCache | None = None,
    ) -> None:
        self._client = client
        self._cache = cache

    async def get_historical(
        self, request: HistoricalRequest
    ) -> HistoricalResponse:
        """Fetch historical data; results cached with 24-hour TTL."""
        cache_key = self._cache_key(request)

        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                try:
                    return HistoricalResponse.model_validate(cached)
                except Exception:
                    pass

        response = await self._fetch(request)

        if self._cache:
            await self._cache.set(
                cache_key,
                response.model_dump(mode="json"),
                ttl=86_400,  # 24 h — historical data never changes
            )

        return response

    async def get_seasonal_average(
        self,
        location: WeatherLocation,
        month: int,
        years: int = 10,
    ) -> dict[str, float]:
        """Return average temperature and precipitation for a given *month*
        aggregated over the last *years* years.

        Returns a dict with keys: ``avg_temp_max_c``, ``avg_temp_min_c``,
        ``total_precip_mm``.
        """
        from datetime import timedelta

        today = date.today()
        records: list[DailyForecast] = []

        for yr in range(today.year - years, today.year):
            start = date(yr, month, 1)
            # last day of month
            if month == 12:
                end = date(yr, 12, 31)
            else:
                end = date(yr, month + 1, 1) - timedelta(days=1)

            try:
                resp = await self.get_historical(
                    HistoricalRequest(
                        location=location,
                        start_date=start,
                        end_date=end,
                    )
                )
                records.extend(resp.daily)
            except HistoricalServiceError:
                continue

        if not records:
            return {}

        return {
            "avg_temp_max_c": sum(r.temp_max_c for r in records) / len(records),
            "avg_temp_min_c": sum(r.temp_min_c for r in records) / len(records),
            "total_precip_mm": sum(r.precipitation_mm for r in records),
            "sample_days": len(records),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _fetch(self, request: HistoricalRequest) -> HistoricalResponse:
        loc = request.location
        params: dict[str, Any] = {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "daily": ",".join(_HIST_DAILY),
            "timezone": request.timezone,
            "windspeed_unit": "kmh",
        }
        if request.include_hourly:
            params["hourly"] = ",".join(_HIST_HOURLY)

        try:
            data = await self._client.get(_ARCHIVE_BASE, "archive", params)
        except WeatherClientError as exc:
            raise HistoricalServiceError(
                f"Archive fetch failed for {loc.name}: {exc}"
            ) from exc

        daily = self._parse_daily(data)
        if request.include_hourly:
            hourly_by_date = self._parse_hourly(data)
            for day in daily:
                day.hourly = hourly_by_date.get(day.date, [])

        return HistoricalResponse(
            location=loc,
            start_date=request.start_date,
            end_date=request.end_date,
            daily=daily,
        )

    def _parse_daily(self, data: dict[str, Any]) -> list[DailyForecast]:
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        results: list[DailyForecast] = []

        for i, d in enumerate(dates):
            wmo = _idx(daily, "weathercode", i, 0)
            results.append(
                DailyForecast(
                    date=date.fromisoformat(d),
                    temp_max_c=float(_idx(daily, "temperature_2m_max", i, 0)),
                    temp_min_c=float(_idx(daily, "temperature_2m_min", i, 0)),
                    precipitation_mm=float(_idx(daily, "precipitation_sum", i, 0)),
                    wind_speed_max_kmh=float(
                        _idx(daily, "windspeed_10m_max", i, 0)
                    ),
                    condition=condition_from_wmo(int(wmo or 0)),
                    sunrise=_parse_dt(_idx(daily, "sunrise", i, None)),
                    sunset=_parse_dt(_idx(daily, "sunset", i, None)),
                    et0_mm=_opt_float(_idx(daily, "et0_fao_evapotranspiration", i, None)),
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
                wind_speed_kmh=float(_idx(hourly, "windspeed_10m", i, 0)),
                condition=condition_from_wmo(int(wmo or 0)),
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
            by_date.setdefault(ts.date(), []).append(hf)

        return by_date

    @staticmethod
    def _cache_key(request: HistoricalRequest) -> str:
        raw = (
            f"{request.location.latitude:.3f}:{request.location.longitude:.3f}:"
            f"{request.start_date}:{request.end_date}:{request.include_hourly}"
        )
        return "hist:" + hashlib.md5(raw.encode()).hexdigest()[:12]


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
