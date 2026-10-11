"""Redis-backed weather data cache with in-memory fallback.

Uses a two-level strategy:
  1. In-process LRU dict (sub-millisecond, no serialisation overhead)
  2. Redis (shared across workers, survives restarts)

Falls back gracefully to in-memory-only when Redis is unavailable.
"""

from __future__ import annotations

import json
import logging
import time
from collections import OrderedDict
from typing import Any

__all__ = [
    "WeatherCache",
    "WeatherCacheError",
]

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 1800  # 30 minutes
_L1_MAX_SIZE = 256   # max entries in the in-process LRU


class WeatherCacheError(Exception):
    """Raised on unrecoverable cache backend errors."""


class _L1Cache:
    """Tiny in-process LRU cache (OrderedDict-based)."""

    def __init__(self, maxsize: int = _L1_MAX_SIZE) -> None:
        self._data: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._maxsize = maxsize

    def get(self, key: str) -> Any | None:
        entry = self._data.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._data[key]
            return None
        self._data.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = (value, time.monotonic() + ttl)
        while len(self._data) > self._maxsize:
            self._data.popitem(last=False)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()

    def __len__(self) -> int:
        return len(self._data)


class WeatherCache:
    """Two-level (L1 in-process + L2 Redis) cache for weather API responses.

    Parameters
    ----------
    redis_url:
        Redis connection URL (e.g. ``"redis://localhost:6379/0"``).
        Pass ``None`` to run in-memory only.
    default_ttl:
        Default time-to-live in seconds (default 1800 = 30 min).
    key_prefix:
        String prepended to every Redis key to avoid collisions.
    """

    def __init__(
        self,
        redis_url: str | None = None,
        *,
        default_ttl: int = _DEFAULT_TTL,
        key_prefix: str = "km:weather:",
    ) -> None:
        self._ttl = default_ttl
        self._prefix = key_prefix
        self._l1 = _L1Cache()
        self._redis: Any = None  # redis.asyncio.Redis | None

        if redis_url:
            try:
                import redis.asyncio as aioredis  # type: ignore[import-untyped]

                self._redis = aioredis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                logger.info("WeatherCache: Redis backend at %s", redis_url)
            except ImportError:
                logger.warning(
                    "WeatherCache: redis package not installed; "
                    "running in-memory only."
                )
            except Exception as exc:
                logger.warning("WeatherCache: Redis init failed (%s); in-memory only.", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get(self, key: str) -> Any | None:
        """Return cached value or *None* if missing/expired."""
        full_key = self._prefix + key

        # L1 hit
        val = self._l1.get(full_key)
        if val is not None:
            return val

        # L2 (Redis) hit
        if self._redis is not None:
            try:
                raw = await self._redis.get(full_key)
                if raw is not None:
                    val = json.loads(raw)
                    # Populate L1 with remaining TTL unknown → use default
                    self._l1.set(full_key, val, self._ttl)
                    return val
            except Exception as exc:
                logger.debug("WeatherCache Redis GET error: %s", exc)

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Store *value* under *key* with optional *ttl* (seconds)."""
        full_key = self._prefix + key
        effective_ttl = ttl if ttl is not None else self._ttl

        self._l1.set(full_key, value, effective_ttl)

        if self._redis is not None:
            try:
                await self._redis.set(
                    full_key,
                    json.dumps(value, default=str),
                    ex=effective_ttl,
                )
            except Exception as exc:
                logger.debug("WeatherCache Redis SET error: %s", exc)

    async def delete(self, key: str) -> None:
        """Evict a key from both cache levels."""
        full_key = self._prefix + key
        self._l1.delete(full_key)
        if self._redis is not None:
            try:
                await self._redis.delete(full_key)
            except Exception as exc:
                logger.debug("WeatherCache Redis DELETE error: %s", exc)

    async def clear_prefix(self, prefix: str) -> int:
        """Delete all keys whose cache key starts with *prefix*. Returns count."""
        full_prefix = self._prefix + prefix
        deleted = 0

        # L1 sweep
        keys_to_del = [k for k in list(self._l1._data) if k.startswith(full_prefix)]
        for k in keys_to_del:
            self._l1.delete(k)
        deleted += len(keys_to_del)

        # Redis SCAN + DEL
        if self._redis is not None:
            try:
                cursor = 0
                pattern = full_prefix + "*"
                while True:
                    cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self._redis.delete(*keys)
                        deleted += len(keys)
                    if cursor == 0:
                        break
            except Exception as exc:
                logger.debug("WeatherCache Redis SCAN error: %s", exc)

        return deleted

    async def ping(self) -> bool:
        """Return *True* if the Redis backend is reachable."""
        if self._redis is None:
            return False
        try:
            return await self._redis.ping()
        except Exception:
            return False

    async def aclose(self) -> None:
        """Close Redis connection pool."""
        if self._redis is not None:
            try:
                await self._redis.aclose()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> WeatherCache:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def l1_size(self) -> int:
        return len(self._l1)

    @property
    def has_redis(self) -> bool:
        return self._redis is not None
