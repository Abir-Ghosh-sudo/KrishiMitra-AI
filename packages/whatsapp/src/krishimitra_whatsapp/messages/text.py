"""WhatsApp text message models for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass

_MAX_TEXT_LENGTH = 4096


@dataclass(frozen=True, slots=True)
class TextMessage:
    """Normalized incoming WhatsApp text message."""

    message_id: str
    sender_id: str
    text: str
    context_message_id: str | None = None
    timestamp: str | None = None


class TextMessageBuilder:
    """Build validated immutable WhatsApp text messages."""

    def build(
        self,
        *,
        message_id: str,
        sender_id: str,
        text: str,
        context_message_id: str | None = None,
        timestamp: str | None = None,
    ) -> TextMessage:
        normalized_message_id = self._required_string(
            message_id,
            field_name="message_id",
        )
        normalized_sender_id = self._required_string(
            sender_id,
            field_name="sender_id",
        )
        normalized_text = self._text(text)

        normalized_context_message_id = self._optional_string(
            context_message_id,
            field_name="context_message_id",
        )
        normalized_timestamp = self._optional_string(
            timestamp,
            field_name="timestamp",
        )

        return TextMessage(
            message_id=normalized_message_id,
            sender_id=normalized_sender_id,
            text=normalized_text,
            context_message_id=normalized_context_message_id,
            timestamp=normalized_timestamp,
        )

    @staticmethod
    def _required_string(value: str, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        normalized = value.strip()

        if not normalized:
            raise ValueError(f"{field_name} must not be empty")

        return normalized

    @staticmethod
    def _optional_string(
        value: str | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string or None")

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _text(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("text must be a string")

        normalized = value.strip()

        if not normalized:
            raise ValueError("text must not be empty")

        if len(normalized) > _MAX_TEXT_LENGTH:
            raise ValueError(
                f"text must not exceed {_MAX_TEXT_LENGTH} characters"
            )

        return normalized


def build_text_message(
    *,
    message_id: str,
    sender_id: str,
    text: str,
    context_message_id: str | None = None,
    timestamp: str | None = None,
) -> TextMessage:
    """Build a validated WhatsApp text message."""

    return TextMessageBuilder().build(
        message_id=message_id,
        sender_id=sender_id,
        text=text,
        context_message_id=context_message_id,
        timestamp=timestamp,
    )


__all__ = [
    "TextMessage",
    "TextMessageBuilder",
    "build_text_message",
]