"""Event publishing primitives for KrishiMitra-AI."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from krishimitra_contracts.events import DomainEvent


EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventPublisher:
    """In-process event publisher with asynchronous subscribers.

    The publisher provides a small abstraction that can later be backed by
    Redis, a message broker, or another event transport without changing
    service-level event contracts.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """Register an asynchronous handler for an event type."""

        handlers = self._subscribers.setdefault(event_type, [])

        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """Remove a previously registered handler."""

        handlers = self._subscribers.get(event_type)

        if not handlers:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._subscribers.pop(event_type, None)

    async def publish(
        self,
        event: DomainEvent,
    ) -> int:
        """Publish an event to all subscribed handlers.

        Returns:
            Number of handlers that successfully completed.
        """

        event_type = event.event_type.value
        handlers = tuple(self._subscribers.get(event_type, ()))

        completed = 0

        for handler in handlers:
            await handler(event)
            completed += 1

        return completed

    def subscriber_count(
        self,
        event_type: str | None = None,
    ) -> int:
        """Return the number of registered subscribers."""

        if event_type is not None:
            return len(self._subscribers.get(event_type, ()))

        return sum(
            len(handlers)
            for handlers in self._subscribers.values()
        )

    def clear(self) -> None:
        """Remove all registered subscribers."""

        self._subscribers.clear()


__all__ = [
    "EventHandler",
    "EventPublisher",
]