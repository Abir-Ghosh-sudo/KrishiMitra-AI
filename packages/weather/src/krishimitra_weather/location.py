"""Location resolution and geocoding for KrishiMitra-AI weather services.

Resolves free-text place names (village, district, state) or raw
lat/lon pairs into a normalised :class:`WeatherLocation` used by every
other weather sub-module.

Backend: Nominatim (OpenStreetMap) — free, no API key required.
Results are cached in-memory with a simple TTL to respect the
Nominatim usage policy (max 1 req/s).
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import NamedTuple

from pydantic import BaseModel, Field, field_validator, model_validator

from .client import WeatherClient, WeatherClientError

__all__ = [
    "Coordinates",
    "LocationError",
    "LocationResolver",
    "WeatherLocation",
]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Nominatim rate-limit: 1 request per second (per TOS)
# ---------------------------------------------------------------------------
_MIN_INTERVAL = 1.05  # slightly above 1 s to be safe


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class Coordinates(NamedTuple):
    """Immutable lat/lon pair."""

    latitude: float
    longitude: float

    def __str__(self) -> str:
        return f"{self.latitude:.4f},{self.longitude:.4f}"


class WeatherLocation(BaseModel):
    """Normalised location descriptor used across all weather modules.

    Attributes
    ----------
    name:
        Human-readable place name (e.g. "Pune, Maharashtra, India").
    latitude:
        WGS-84 latitude in decimal degrees (−90 … +90).
    longitude:
        WGS-84 longitude in decimal degrees (−180 … +180).
    state:
        State / province extracted from Nominatim address components.
    country:
        ISO 3166-1 alpha-2 country code (lower-case), e.g. ``"in"``.
    elevation_m:
        Elevation above sea level in metres (optional).
    timezone:
        IANA timezone string, e.g. ``"Asia/Kolkata"`` (optional).
    """

    name: str = Field(..., min_length=1, description="Display name of the location.")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    state: str | None = Field(default=None)
    country: str | None = Field(default=None, max_length=2)
    elevation_m: float | None = Field(default=None, ge=-500.0, le=9000.0)
    timezone: str | None = Field(default=None)

    @field_validator("country", mode="before")
    @classmethod
    def _normalise_country(cls, v: object) -> str | None:
        if isinstance(v, str):
            return v.lower()[:2] or None
        return None

    @property
    def coordinates(self) -> Coordinates:
        return Coordinates(latitude=self.latitude, longitude=self.longitude)

    def __str__(self) -> str:
        return self.name

    model_config = {"frozen": True}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class LocationError(Exception):
    """Raised when a location cannot be resolved."""


# ---------------------------------------------------------------------------
# In-memory geocoding cache entry
# ---------------------------------------------------------------------------


class _CacheEntry(NamedTuple):
    location: WeatherLocation
    expires_at: float  # monotonic timestamp


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

# Regex for bare "lat,lon" or "lat lon" inputs
_COORD_RE = re.compile(
    r"^\s*(?P<lat>-?\d{1,3}(?:\.\d+)?)\s*[,\s]\s*(?P<lon>-?\d{1,3}(?:\.\d+)?)\s*$"
)


class LocationResolver:
    """Resolves place names and coordinates to :class:`WeatherLocation` objects.

    Parameters
    ----------
    client:
        Shared :class:`~krishimitra_weather.client.WeatherClient` instance.
    cache_ttl:
        Seconds to cache each geocoding result (default 6 hours).
    default_country:
        ISO 3166-1 alpha-2 code appended to queries to bias results
        (default ``"in"`` for India).
    """

    def __init__(
        self,
        client: WeatherClient,
        *,
        cache_ttl: float = 6 * 3600,
        default_country: str = "in",
    ) -> None:
        self._client = client
        self._cache_ttl = cache_ttl
        self._default_country = default_country.lower()
        self._cache: dict[str, _CacheEntry] = {}
        self._last_request_at: float = 0.0
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def resolve(self, query: str) -> WeatherLocation:
        """Resolve *query* to a :class:`WeatherLocation`.

        *query* may be:
        - A free-text place name: ``"Nashik, Maharashtra"``
        - A ``"lat,lon"`` string: ``"20.0,73.8"``

        Results are cached for :attr:`cache_ttl` seconds.

        Raises
        ------
        LocationError
            If the place cannot be found or the API call fails.
        """
        key = query.strip().lower()

        # 1. Memory cache hit
        if entry := self._cache.get(key):
            if time.monotonic() < entry.expires_at:
                logger.debug("Location cache hit: %r", key)
                return entry.location
            del self._cache[key]

        # 2. Try parsing as raw coordinates first (no network call needed)
        if coord_match := _COORD_RE.match(query):
            lat = float(coord_match.group("lat"))
            lon = float(coord_match.group("lon"))
            location = await self._reverse_geocode(lat, lon)
            self._store(key, location)
            return location

        # 3. Forward geocoding via Nominatim
        location = await self._forward_geocode(query)
        self._store(key, location)
        return location

    async def resolve_coordinates(
        self,
        latitude: float,
        longitude: float,
    ) -> WeatherLocation:
        """Reverse-geocode raw *latitude* / *longitude* to a location."""
        key = f"{latitude:.4f},{longitude:.4f}"
        if entry := self._cache.get(key):
            if time.monotonic() < entry.expires_at:
                return entry.location
            del self._cache[key]

        location = await self._reverse_geocode(latitude, longitude)
        self._store(key, location)
        return location

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _forward_geocode(self, query: str) -> WeatherLocation:
        """Call Nominatim /search and parse first result."""
        async with self._lock:
            await self._rate_limit()
            try:
                data = await self._client.nominatim(
                    "search",
                    params={
                        "q": query,
                        "format": "jsonv2",
                        "addressdetails": "1",
                        "limit": "1",
                        "countrycodes": self._default_country,
                    },
                )
            except WeatherClientError as exc:
                raise LocationError(
                    f"Geocoding API error for {query!r}: {exc}"
                ) from exc

        results: list[dict] = data if isinstance(data, list) else []  # type: ignore[assignment]
        if not results:
            # Retry without country bias
            async with self._lock:
                await self._rate_limit()
                try:
                    data = await self._client.nominatim(
                        "search",
                        params={
                            "q": query,
                            "format": "jsonv2",
                            "addressdetails": "1",
                            "limit": "1",
                        },
                    )
                except WeatherClientError as exc:
                    raise LocationError(
                        f"Geocoding API error for {query!r}: {exc}"
                    ) from exc
            results = data if isinstance(data, list) else []  # type: ignore[assignment]

        if not results:
            raise LocationError(
                f"No location found for query: {query!r}"
            )

        return self._parse_search_result(results[0])

    async def _reverse_geocode(
        self,
        lat: float,
        lon: float,
    ) -> WeatherLocation:
        """Call Nominatim /reverse and parse result."""
        async with self._lock:
            await self._rate_limit()
            try:
                data = await self._client.nominatim(
                    "reverse",
                    params={
                        "lat": str(lat),
                        "lon": str(lon),
                        "format": "jsonv2",
                        "addressdetails": "1",
                    },
                )
            except WeatherClientError as exc:
                raise LocationError(
                    f"Reverse geocoding failed for ({lat}, {lon}): {exc}"
                ) from exc

        result: dict = data if isinstance(data, dict) else {}  # type: ignore[assignment]
        if not result or "error" in result:
            raise LocationError(
                f"No result for coordinates ({lat}, {lon}): {result.get('error', 'unknown')}"
            )

        return self._parse_search_result(result)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_search_result(self, result: dict) -> WeatherLocation:  # type: ignore[type-arg]
        """Extract :class:`WeatherLocation` from a Nominatim result dict."""
        address: dict = result.get("address", {})  # type: ignore[type-arg]

        display_name: str = result.get("display_name", "Unknown")
        lat = float(result.get("lat", 0.0))
        lon = float(result.get("lon", 0.0))

        state: str | None = (
            address.get("state")
            or address.get("province")
            or address.get("county")
            or None
        )
        country_code: str | None = address.get("country_code") or None

        return WeatherLocation(
            name=display_name,
            latitude=lat,
            longitude=lon,
            state=state,
            country=country_code,
        )

    async def _rate_limit(self) -> None:
        """Enforce Nominatim 1-req/s limit. Must be called under self._lock."""
        now = time.monotonic()
        elapsed = now - self._last_request_at
        if elapsed < _MIN_INTERVAL:
            await asyncio.sleep(_MIN_INTERVAL - elapsed)
        self._last_request_at = time.monotonic()

    def _store(self, key: str, location: WeatherLocation) -> None:
        self._cache[key] = _CacheEntry(
            location=location,
            expires_at=time.monotonic() + self._cache_ttl,
        )

    def invalidate_cache(self) -> None:
        """Clear all cached geocoding results."""
        self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Number of currently cached location entries."""
        return len(self._cache)
