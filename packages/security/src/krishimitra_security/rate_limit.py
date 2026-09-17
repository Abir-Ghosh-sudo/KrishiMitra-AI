"""Rate limiting primitives for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    """Result of a rate-limit check."""

    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: float | None = None


@dataclass(slots=True)
class _Bucket:
    """Internal token-bucket state."""

    tokens: float
    last_refill: float


class TokenBucketRateLimiter:
    """Thread-safe token-bucket rate limiter.

    This is an application-level primitive. For a multi-instance deployment,
    the bucket state should be backed by a shared store such as Redis.
    """

    def __init__(
        self,
        *,
        limit: int,
        window_seconds: float,
    ) -> None:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")

        self._limit = limit
        self._window_seconds = window_seconds
        self._refill_rate = limit / window_seconds

        self._buckets: dict[str, _Bucket] = {}
        self._lock = Lock()

    def _refill(
        self,
        bucket: _Bucket,
        now: float,
    ) -> None:
        elapsed = max(0.0, now - bucket.last_refill)

        if elapsed <= 0:
            return

        bucket.tokens = min(
            float(self._limit),
            bucket.tokens + elapsed * self._refill_rate,
        )

        bucket.last_refill = now

    def check(
        self,
        key: str,
        *,
        consume: bool = True,
    ) -> RateLimitDecision:
        """Check whether a request is allowed.

        Args:
            key: Identifier being rate limited, such as a user or IP.
            consume: Whether an allowed request consumes one token.
        """

        normalized_key = key.strip()

        if not normalized_key:
            raise ValueError("rate-limit key must not be empty")

        now = monotonic()

        with self._lock:
            bucket = self._buckets.get(normalized_key)

            if bucket is None:
                bucket = _Bucket(
                    tokens=float(self._limit),
                    last_refill=now,
                )
                self._buckets[normalized_key] = bucket

            self._refill(bucket, now)

            if bucket.tokens >= 1.0:
                if consume:
                    bucket.tokens -= 1.0

                return RateLimitDecision(
                    allowed=True,
                    limit=self._limit,
                    remaining=max(0, int(bucket.tokens)),
                )

            retry_after = (1.0 - bucket.tokens) / self._refill_rate

            return RateLimitDecision(
                allowed=False,
                limit=self._limit,
                remaining=0,
                retry_after_seconds=retry_after,
            )

    def reset(
        self,
        key: str,
    ) -> bool:
        """Reset rate-limit state for a key."""

        normalized_key = key.strip()

        if not normalized_key:
            raise ValueError("rate-limit key must not be empty")

        with self._lock:
            return self._buckets.pop(normalized_key, None) is not None

    def clear(self) -> None:
        """Clear all tracked rate-limit buckets."""

        with self._lock:
            self._buckets.clear()

    @property
    def limit(self) -> int:
        """Return the configured request capacity."""

        return self._limit

    @property
    def window_seconds(self) -> float:
        """Return the configured refill window."""

        return self._window_seconds


__all__ = [
    "RateLimitDecision",
    "TokenBucketRateLimiter",
]