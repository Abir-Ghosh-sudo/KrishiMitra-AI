from __future__ import annotations
import asyncio
import time

class LockError(Exception):
    pass

class DistributedLock:
    """Simple asyncio-based distributed lock backed by Redis."""
    def __init__(self, redis_client: object, name: str, *, ttl: int = 30) -> None:
        self._redis = redis_client
        self._name = f"lock:{name}"
        self._ttl = ttl

    async def acquire(self, timeout: float = 5.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._redis is not None:
                try:
                    result = await self._redis.set(self._name, "1", ex=self._ttl, nx=True)
                    if result:
                        return True
                except Exception:
                    pass
            await asyncio.sleep(0.1)
        return False

    async def release(self) -> None:
        if self._redis is not None:
            try:
                await self._redis.delete(self._name)
            except Exception:
                pass

    async def __aenter__(self) -> "DistributedLock":
        if not await self.acquire():
            raise LockError(f"Could not acquire lock: {self._name}")
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.release()

__all__ = ["DistributedLock", "LockError"]
