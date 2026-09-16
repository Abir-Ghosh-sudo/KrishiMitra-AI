"""Event consuming primitives for KrishiMitra-AI."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from krishimitra_contracts.events import DomainEvent


EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventConsumer:
    """Asynchronous in-process event consumer.

    This abstraction keeps event handling independent from the underlying
    transport. A production transport such as Redis, RabbitMQ, or another
    broker can invoke ``consume`` with the same DomainEvent contract.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, EventHandler] = {}

    def register(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """Register a handler for an event type."""

        if not event_type.strip():
            raise ValueError("event_type must not be empty")

        self._handlers[event_type] = handler

    def unregister(
        self,
        event_type: str,
    ) -> None:
        """Remove the handler registered for an event type."""

        self._handlers.pop(event_type, None)

    async def consume(
        self,
        event: DomainEvent,
    ) -> bool:
        """Consume an event using its registered handler.

        Returns:
            ``True`` when a handler processed the event, otherwise ``False``.
        """

        handler = self._handlers.get(event.event_type.value)

        if handler is None:
            return False

        await handler(event)
        return True

    def has_handler(
        self,
        event_type: str,
    ) -> bool:
        """Return whether a handler exists for an event type."""

        return event_type in self._handlers

    def handler_count(self) -> int:
        """Return the number of registered event handlers."""

        return len(self._handlers)

    def clear(self) -> None:
        """Remove all registered handlers."""

        self._handlers.clear()


__all__ = [
    "EventConsumer",
    "EventHandler",
]