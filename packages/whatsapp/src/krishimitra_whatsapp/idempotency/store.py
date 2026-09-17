"""Idempotency storage primitives for WhatsApp message processing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from threading import RLock


class IdempotencyState(StrEnum):
    """Lifecycle states for an idempotency record."""

    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    """Stored state for one idempotent operation."""

    key: str
    state: IdempotencyState
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    response_reference: str | None = None
    error_code: str | None = None


class IdempotencyStore:
    """Thread-safe in-memory idempotency store.

    This class provides the application-level contract needed by the
    WhatsApp processing pipeline. Production deployments should back the
    same semantics with PostgreSQL or Redis so idempotency is shared
    across API and worker instances.
    """

    def __init__(
        self,
        *,
        ttl_seconds: int = 86_400,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero")

        self._ttl = timedelta(seconds=ttl_seconds)
        self._records: dict[str, IdempotencyRecord] = {}
        self._lock = RLock()

    def get(
        self,
        key: str,
    ) -> IdempotencyRecord | None:
        """Return a non-expired record for a key."""

        normalized_key = self._normalize_key(key)

        with self._lock:
            self._remove_if_expired(normalized_key)

            return self._records.get(normalized_key)

    def exists(
        self,
        key: str,
    ) -> bool:
        """Return whether a non-expired record exists."""

        return self.get(key) is not None

    def start(
        self,
        key: str,
    ) -> IdempotencyRecord:
        """Create a processing record.

        Raises:
            ValueError: If the key already exists and has not expired.
        """

        normalized_key = self._normalize_key(key)
        now = self._now()

        with self._lock:
            self._remove_if_expired(normalized_key)

            if normalized_key in self._records:
                raise ValueError(
                    "idempotency key already exists",
                )

            record = IdempotencyRecord(
                key=normalized_key,
                state=IdempotencyState.PROCESSING,
                created_at=now,
                updated_at=now,
                expires_at=now + self._ttl,
            )

            self._records[normalized_key] = record

            return record

    def mark_completed(
        self,
        key: str,
        *,
        response_reference: str | None = None,
    ) -> IdempotencyRecord:
        """Mark a processing operation as successfully completed."""

        return self._update(
            key,
            state=IdempotencyState.COMPLETED,
            response_reference=response_reference,
            error_code=None,
        )

    def mark_failed(
        self,
        key: str,
        *,
        error_code: str | None = None,
    ) -> IdempotencyRecord:
        """Mark a processing operation as failed."""

        return self._update(
            key,
            state=IdempotencyState.FAILED,
            response_reference=None,
            error_code=error_code,
        )

    def delete(
        self,
        key: str,
    ) -> bool:
        """Delete an idempotency record."""

        normalized_key = self._normalize_key(key)

        with self._lock:
            return self._records.pop(
                normalized_key,
                None,
            ) is not None

    def cleanup_expired(self) -> int:
        """Remove all expired records and return the number removed."""

        now = self._now()

        with self._lock:
            expired_keys = [
                key
                for key, record in self._records.items()
                if record.expires_at <= now
            ]

            for key in expired_keys:
                del self._records[key]

            return len(expired_keys)

    def size(self) -> int:
        """Return the number of currently stored records."""

        self.cleanup_expired()

        with self._lock:
            return len(self._records)

    def clear(self) -> None:
        """Remove all stored records."""

        with self._lock:
            self._records.clear()

    def _update(
        self,
        key: str,
        *,
        state: IdempotencyState,
        response_reference: str | None,
        error_code: str | None,
    ) -> IdempotencyRecord:
        normalized_key = self._normalize_key(key)
        now = self._now()

        with self._lock:
            self._remove_if_expired(normalized_key)

            current = self._records.get(normalized_key)

            if current is None:
                raise KeyError(
                    "idempotency key does not exist",
                )

            record = IdempotencyRecord(
                key=current.key,
                state=state,
                created_at=current.created_at,
                updated_at=now,
                expires_at=current.expires_at,
                response_reference=response_reference,
                error_code=error_code,
            )

            self._records[normalized_key] = record

            return record

    def _remove_if_expired(
        self,
        key: str,
    ) -> None:
        record = self._records.get(key)

        if record is None:
            return

        if record.expires_at <= self._now():
            del self._records[key]

    @staticmethod
    def _normalize_key(key: str) -> str:
        if not isinstance(key, str):
            raise TypeError("idempotency key must be a string")

        normalized = key.strip()

        if not normalized:
            raise ValueError(
                "idempotency key must not be empty",
            )

        if len(normalized) > 512:
            raise ValueError(
                "idempotency key must not exceed 512 characters",
            )

        return normalized

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)


__all__ = [
    "IdempotencyRecord",
    "IdempotencyState",
    "IdempotencyStore",
]