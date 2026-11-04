from __future__ import annotations
import time
from collections import deque

class RateLimitExceeded(Exception):
    pass

class RateLimiter:
    """In-process sliding-window rate limiter."""
    def __init__(self, max_calls: int, window_seconds: float) -> None:
        self._max = max_calls
        self._window = window_seconds
        self._calls: deque[float] = deque()

    def check(self, key: str = "") -> bool:
        now = time.monotonic()
        while self._calls and now - self._calls[0] > self._window:
            self._calls.popleft()
        if len(self._calls) >= self._max:
            return False
        self._calls.append(now)
        return True

    def require(self, key: str = "") -> None:
        if not self.check(key):
            raise RateLimitExceeded(f"Rate limit exceeded: {self._max} calls per {self._window}s")

__all__ = ["RateLimiter", "RateLimitExceeded"]
