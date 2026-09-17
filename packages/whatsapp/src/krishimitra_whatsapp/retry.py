"""Retry utilities for WhatsApp integration."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """Configuration for bounded exponential-backoff retries."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 10.0
    jitter: bool = True

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must be non-negative")

        if self.max_delay_seconds < 0:
            raise ValueError("max_delay_seconds must be non-negative")

        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError(
                "max_delay_seconds must be greater than or equal to "
                "base_delay_seconds"
            )


class RetryExhaustedError(Exception):
    """Raised when all retry attempts fail."""

    def __init__(
        self,
        *,
        attempts: int,
        last_error: Exception,
    ) -> None:
        self.attempts = attempts
        self.last_error = last_error

        super().__init__(
            f"Operation failed after {attempts} attempt(s): "
            f"{last_error}"
        )


def calculate_backoff(
    attempt: int,
    *,
    config: RetryConfig | None = None,
) -> float:
    """Calculate exponential-backoff delay for a retry attempt."""

    retry_config = config or RetryConfig()

    if attempt < 1:
        raise ValueError("attempt must be at least 1")

    exponential_delay = retry_config.base_delay_seconds * (2 ** (attempt - 1))
    delay = min(
        exponential_delay,
        retry_config.max_delay_seconds,
    )

    if retry_config.jitter and delay > 0:
        delay = random.uniform(0, delay)

    return delay


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    config: RetryConfig | None = None,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Execute an async operation with bounded retries."""

    retry_config = config or RetryConfig()

    if not callable(operation):
        raise TypeError("operation must be callable")

    if not retryable_exceptions:
        raise ValueError("retryable_exceptions must not be empty")

    last_error: Exception | None = None

    for attempt in range(1, retry_config.max_attempts + 1):
        try:
            return await operation()
        except retryable_exceptions as exc:
            last_error = exc

            if attempt >= retry_config.max_attempts:
                break

            delay = calculate_backoff(
                attempt,
                config=retry_config,
            )

            if delay > 0:
                await asyncio.sleep(delay)

    assert last_error is not None

    raise RetryExhaustedError(
        attempts=retry_config.max_attempts,
        last_error=last_error,
    ) from last_error


__all__ = [
    "RetryConfig",
    "RetryExhaustedError",
    "calculate_backoff",
    "retry_async",
]