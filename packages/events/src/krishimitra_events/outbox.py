"""Transactional outbox primitives for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from krishimitra_contracts.events import DomainEvent, EventMetadata, EventType


class OutboxStatus(StrEnum):
    """Lifecycle status of an outbox event."""

    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"


class OutboxEvent:
    """Persistent-ready representation of an event in the outbox."""

    def __init__(
        self,
        event: DomainEvent,
        *,
        outbox_id: UUID | None = None,
        status: OutboxStatus = OutboxStatus.PENDING,
        attempts: int = 0,
        last_error: str | None = None,
        published_at: datetime | None = None,
    ) -> None:
        self.outbox_id = outbox_id or uuid4()
        self.event = event
        self.status = status
        self.attempts = attempts
        self.last_error = last_error
        self.published_at = published_at

    def mark_processing(self) -> None:
        """Mark the event as currently being published."""

        self.status = OutboxStatus.PROCESSING
        self.attempts += 1

    def mark_published(
        self,
        published_at: datetime | None = None,
    ) -> None:
        """Mark the event as successfully published."""

        self.status = OutboxStatus.PUBLISHED
        self.published_at = published_at or datetime.now(timezone.utc)
        self.last_error = None

    def mark_failed(
        self,
        error: str,
    ) -> None:
        """Mark the event as failed and retain the error."""

        self.status = OutboxStatus.FAILED
        self.last_error = error[:2000]


class OutboxStore:
    """Small in-memory outbox store.

    This is an application-level abstraction. The production implementation
    can persist the same lifecycle in PostgreSQL inside the originating
    transaction.
    """

    def __init__(self) -> None:
        self._events: dict[UUID, OutboxEvent] = {}

    def add(
        self,
        event: DomainEvent,
    ) -> OutboxEvent:
        """Add an event to the outbox."""

        record = OutboxEvent(event)
        self._events[record.outbox_id] = record
        return record

    def get(
        self,
        outbox_id: UUID,
    ) -> OutboxEvent | None:
        """Return an outbox event by identifier."""

        return self._events.get(outbox_id)

    def pending(
        self,
        *,
        limit: int = 100,
    ) -> tuple[OutboxEvent, ...]:
        """Return pending events up to the requested limit."""

        if limit < 1:
            raise ValueError("limit must be greater than zero")

        events = (
            record
            for record in self._events.values()
            if record.status is OutboxStatus.PENDING
        )

        return tuple(events)[:limit]

    def remove(
        self,
        outbox_id: UUID,
    ) -> bool:
        """Remove an outbox record."""

        return self._events.pop(outbox_id, None) is not None

    def count(
        self,
        status: OutboxStatus | None = None,
    ) -> int:
        """Return the number of stored records."""

        if status is None:
            return len(self._events)

        return sum(
            record.status is status
            for record in self._events.values()
        )

    def clear(self) -> None:
        """Remove all stored outbox records."""

        self._events.clear()


__all__ = [
    "OutboxEvent",
    "OutboxStatus",
    "OutboxStore",
]