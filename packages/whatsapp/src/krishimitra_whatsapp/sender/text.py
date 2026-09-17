"""WhatsApp text message payload builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_MAX_TEXT_LENGTH = 4096


@dataclass(frozen=True, slots=True)
class TextSendPayload:
    """Validated payload for sending a WhatsApp text message."""

    recipient: str
    text: str
    preview_url: bool = False


class TextPayloadBuilder:
    """Build WhatsApp Cloud API text-message payloads."""

    def build(
        self,
        *,
        recipient: str,
        text: str,
        preview_url: bool = False,
    ) -> TextSendPayload:
        normalized_recipient = self._required_string(
            recipient,
            field_name="recipient",
        )
        normalized_text = self._text(text)

        if not isinstance(preview_url, bool):
            raise TypeError("preview_url must be a boolean")

        return TextSendPayload(
            recipient=normalized_recipient,
            text=normalized_text,
            preview_url=preview_url,
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


def build_text_payload(
    *,
    recipient: str,
    text: str,
    preview_url: bool = False,
) -> dict[str, Any]:
    """Build a WhatsApp Cloud API-compatible text payload."""

    payload = TextPayloadBuilder().build(
        recipient=recipient,
        text=text,
        preview_url=preview_url,
    )

    return {
        "messaging_product": "whatsapp",
        "to": payload.recipient,
        "type": "text",
        "text": {
            "preview_url": payload.preview_url,
            "body": payload.text,
        },
    }


__all__ = [
    "TextPayloadBuilder",
    "TextSendPayload",
    "build_text_payload",
]