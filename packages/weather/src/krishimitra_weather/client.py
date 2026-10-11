"""HTTP client for weather API integration (Open-Meteo + Nominatim geocoding).

Provides a thin, typed async wrapper around httpx with retry logic,
timeout handling, and a Protocol for dependency-injection in tests.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol, runtime_checkable

import httpx

__all__ = [
    "WeatherClient",
    "WeatherClientError",
    "WeatherClientProtocol",
]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public API base URLs (Open-Meteo is free, no key required)
# ---------------------------------------------------------------------------
_OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
_NOMINATIM_BASE = "https://nominatim.openstreetmap.org"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
_DEFAULT_TIMEOUT = 15.0  # seconds
_DEFAULT_RETRIES = 3


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class WeatherClientError(Exception):
    """Raised when the weather HTTP client encounters an unrecoverable error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


# ---------------------------------------------------------------------------
# Protocol (for test doubles / alternative backends)
# ---------------------------------------------------------------------------


@runtime_checkable
class WeatherClientProtocol(Protocol):
    """Structural interface satisfied by :class:`WeatherClient` and fakes."""

    async def get(
        self,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform a GET request and return the decoded JSON body."""
        ...

    async def aclose(self) -> None:
        """Release underlying resources."""
        ...


# ---------------------------------------------------------------------------
# Concrete client
# ---------------------------------------------------------------------------


class WeatherClient:
    """Async HTTP client with retry/back-off for weather API calls.

    Parameters
    ----------
    timeout:
        Request timeout in seconds (default 15 s).
    max_retries:
        Number of times to retry on transient 5xx / network errors.
    user_agent:
        ``User-Agent`` header sent with every request (Nominatim TOS
        requires a descriptive string).
    """

    def __init__(
        self,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_RETRIES,
        user_agent: str = "KrishiMitra-AI/1.0 (agricultural assistant)",
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"User-Agent": user_agent},
            follow_redirects=True,
        )

    # ------------------------------------------------------------------
    # Core method
    # ------------------------------------------------------------------

    async def get(
        self,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """GET *base_url + path* and return the decoded JSON body.

        Raises
        ------
        WeatherClientError
            On HTTP 4xx/5xx or network failure after all retries.
        """
        url = base_url.rstrip("/") + "/" + path.lstrip("/")
        last_exc: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                logger.debug("GET %s attempt=%d params=%s", url, attempt, params)
                response = await self._client.get(url, params=params)
                response.raise_for_status()
                return response.json()  # type: ignore[no-any-return]
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status < 500:
                    # Client errors are not retried
                    raise WeatherClientError(
                        f"HTTP {status} from {url}: {exc.response.text[:200]}",
                        status_code=status,
                    ) from exc
                logger.warning(
                    "HTTP %d from %s (attempt %d/%d)",
                    status,
                    url,
                    attempt,
                    self._max_retries,
                )
                last_exc = exc
            except httpx.RequestError as exc:
                logger.warning(
                    "Network error calling %s (attempt %d/%d): %s",
                    url,
                    attempt,
                    self._max_retries,
                    exc,
                )
                last_exc = exc

        raise WeatherClientError(
            f"Failed to GET {url} after {self._max_retries} attempts: {last_exc}"
        ) from last_exc

    # ------------------------------------------------------------------
    # Convenience helpers (pre-bound to known base URLs)
    # ------------------------------------------------------------------

    async def open_meteo(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call the Open-Meteo API."""
        return await self.get(_OPEN_METEO_BASE, path, params)

    async def nominatim(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Call the Nominatim geocoding API.

        Returns
        -------
        dict or list
            Nominatim may return either depending on the endpoint.
        """
        url = _NOMINATIM_BASE.rstrip("/") + "/" + path.lstrip("/")
        last_exc: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                response = await self._client.get(url, params=params)
                response.raise_for_status()
                return response.json()  # type: ignore[no-any-return]
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status < 500:
                    raise WeatherClientError(
                        f"HTTP {status} from {url}", status_code=status
                    ) from exc
                last_exc = exc
            except httpx.RequestError as exc:
                last_exc = exc
        raise WeatherClientError(
            f"Failed to GET {url} after {self._max_retries} attempts: {last_exc}"
        ) from last_exc

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def aclose(self) -> None:
        """Close the underlying httpx session."""
        await self._client.aclose()

    async def __aenter__(self) -> WeatherClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
