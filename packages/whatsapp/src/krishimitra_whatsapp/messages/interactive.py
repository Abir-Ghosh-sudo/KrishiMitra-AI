"""WhatsApp interactive message models for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InteractiveType(StrEnum):
    """Supported WhatsApp interactive message types."""

    BUTTON_REPLY = "button_reply"
    LIST_REPLY = "list_reply"


@dataclass(frozen=True, slots=True)
class InteractiveMessage:
    """Normalized incoming WhatsApp interactive message."""

    message_id: str
    sender_id: str
    interactive_type: InteractiveType
    reply_id: str
    reply_title: str | None = None
    context_message_id: str | None = None
    timestamp: str | None = None


class InteractiveMessageBuilder:
    """Build validated interactive message objects."""

    def build(
        self,
        *,
        message_id: str,
        sender_id: str,
        interactive_type: InteractiveType | str,
        reply_id: str,
        reply_title: str | None = None,
        context_message_id: str | None = None,
        timestamp: str | None = None,
    ) -> InteractiveMessage:
        """Create a normalized interactive message."""

        return InteractiveMessage(
            message_id=self._required(
                message_id,
                "message_id",
            ),
            sender_id=self._required(
                sender_id,
                "sender_id",
            ),
            interactive_type=self._parse_type(
                interactive_type,
            ),
            reply_id=self._required(
                reply_id,
                "reply_id",
            ),
            reply_title=self._optional(reply_title),
            context_message_id=self._optional(
                context_message_id,
            ),
            timestamp=self._optional(timestamp),
        )

    @staticmethod
    def _parse_type(
        value: InteractiveType | str,
    ) -> InteractiveType:
        if isinstance(value, InteractiveType):
            return value

        if not isinstance(value, str):
            raise TypeError(
                "interactive_type must be a string",
            )

        try:
            return InteractiveType(value.strip())
        except ValueError as exc:
            raise ValueError(
                f"unsupported interactive type: {value}",
            ) from exc

    @staticmethod
    def _required(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string",
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty",
            )

        return normalized

    @staticmethod
    def _optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                "optional message fields must be strings",
            )

        normalized = value.strip()

        return normalized or None


def build_interactive_message(
    *,
    message_id: str,
    sender_id: str,
    interactive_type: InteractiveType | str,
    reply_id: str,
    reply_title: str | None = None,
    context_message_id: str | None = None,
    timestamp: str | None = None,
) -> InteractiveMessage:
    """Build an interactive message using the default builder."""

    return InteractiveMessageBuilder().build(
        message_id=message_id,
        sender_id=sender_id,
        interactive_type=interactive_type,
        reply_id=reply_id,
        reply_title=reply_title,
        context_message_id=context_message_id,
        timestamp=timestamp,
    )


__all__ = [
    "InteractiveMessage",
    "InteractiveMessageBuilder",
    "InteractiveType",
    "build_interactive_message",
]