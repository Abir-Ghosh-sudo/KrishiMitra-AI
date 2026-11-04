from __future__ import annotations
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

class RedisCacheError(Exception):
    pass

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379/0", *, default_ttl: int = 3600) -> None:
        self._url = url
        self._ttl = default_ttl
        self._client: Any = None
        try:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(url, encoding="utf-8", decode_responses=True)
        except ImportError:
            logger.warning("redis package not installed; cache disabled.")

    async def get(self, key: str) -> Any | None:
        if not self._client:
            return None
        try:
            val = await self._client.get(key)
            return json.loads(val) if val is not None else None
        except Exception as exc:
            logger.debug("RedisCache GET error: %s", exc)
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if not self._client:
            return
        try:
            await self._client.set(key, json.dumps(value, default=str), ex=ttl or self._ttl)
        except Exception as exc:
            logger.debug("RedisCache SET error: %s", exc)

    async def delete(self, key: str) -> None:
        if self._client:
            try:
                await self._client.delete(key)
            except Exception:
                pass

    async def aclose(self) -> None:
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass

    async def __aenter__(self) -> "RedisCache":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

__all__ = ["RedisCache", "RedisCacheError"]
