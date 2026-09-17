"""WhatsApp webhook payload parsing for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ParsedMessageType(StrEnum):
    """Supported incoming WhatsApp message types."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"
    VIDEO = "video"
    LOCATION = "location"
    INTERACTIVE = "interactive"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ParsedMessage:
    """Normalized incoming WhatsApp message."""

    message_id: str
    sender_id: str
    message_type: ParsedMessageType
    timestamp: str | None = None
    phone_number_id: str | None = None
    text: str | None = None
    media_id: str | None = None
    mime_type: str | None = None
    filename: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    raw_message: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ParsedWebhook:
    """Normalized result of parsing a webhook payload."""

    messages: tuple[ParsedMessage, ...]
    statuses: tuple[dict[str, Any], ...]


class WebhookPayloadParser:
    """Parse Meta WhatsApp Cloud API webhook payloads."""

    def parse(
        self,
        payload: dict[str, Any],
    ) -> ParsedWebhook:
        """Parse messages and statuses from a webhook payload."""

        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary")

        messages: list[ParsedMessage] = []
        statuses: list[dict[str, Any]] = []

        entries = payload.get("entry", [])

        if not isinstance(entries, list):
            raise ValueError("payload entry must be a list")

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            changes = entry.get("changes", [])

            if not isinstance(changes, list):
                continue

            for change in changes:
                if not isinstance(change, dict):
                    continue

                value = change.get("value")

                if not isinstance(value, dict):
                    continue

                metadata = value.get("metadata", {})

                if not isinstance(metadata, dict):
                    metadata = {}

                phone_number_id = self._string_or_none(
                    metadata.get("phone_number_id"),
                )

                raw_messages = value.get("messages", [])

                if isinstance(raw_messages, list):
                    for raw_message in raw_messages:
                        parsed = self._parse_message(
                            raw_message,
                            phone_number_id,
                        )

                        if parsed is not None:
                            messages.append(parsed)

                raw_statuses = value.get("statuses", [])

                if isinstance(raw_statuses, list):
                    for status in raw_statuses:
                        if isinstance(status, dict):
                            statuses.append(status)

        return ParsedWebhook(
            messages=tuple(messages),
            statuses=tuple(statuses),
        )

    def _parse_message(
        self,
        message: Any,
        phone_number_id: str | None,
    ) -> ParsedMessage | None:
        if not isinstance(message, dict):
            return None

        message_id = self._string_or_none(
            message.get("id"),
        )
        sender_id = self._string_or_none(
            message.get("from"),
        )

        if not message_id or not sender_id:
            return None

        message_type = self._message_type(message)

        common = {
            "message_id": message_id,
            "sender_id": sender_id,
            "message_type": message_type,
            "timestamp": self._string_or_none(
                message.get("timestamp"),
            ),
            "phone_number_id": phone_number_id,
            "raw_message": message,
        }

        if message_type is ParsedMessageType.TEXT:
            text_data = self._dict_or_empty(
                message.get("text"),
            )

            return ParsedMessage(
                **common,
                text=self._string_or_none(
                    text_data.get("body"),
                ),
            )

        if message_type in {
            ParsedMessageType.IMAGE,
            ParsedMessageType.AUDIO,
            ParsedMessageType.DOCUMENT,
            ParsedMessageType.VIDEO,
        }:
            media_data = self._dict_or_empty(
                message.get(message_type.value),
            )

            return ParsedMessage(
                **common,
                media_id=self._string_or_none(
                    media_data.get("id"),
                ),
                mime_type=self._string_or_none(
                    media_data.get("mime_type"),
                ),
                filename=self._string_or_none(
                    media_data.get("filename"),
                ),
            )

        if message_type is ParsedMessageType.LOCATION:
            location = self._dict_or_empty(
                message.get("location"),
            )

            return ParsedMessage(
                **common,
                latitude=self._float_or_none(
                    location.get("latitude"),
                ),
                longitude=self._float_or_none(
                    location.get("longitude"),
                ),
            )

        return ParsedMessage(**common)

    @staticmethod
    def _message_type(
        message: dict[str, Any],
    ) -> ParsedMessageType:
        raw_type = message.get("type")

        try:
            return ParsedMessageType(
                raw_type,
            )
        except ValueError:
            return ParsedMessageType.UNKNOWN

    @staticmethod
    def _dict_or_empty(
        value: Any,
    ) -> dict[str, Any]:
        if isinstance(value, dict):
            return value

        return {}

    @staticmethod
    def _string_or_none(
        value: Any,
    ) -> str | None:
        if isinstance(value, str) and value.strip():
            return value.strip()

        return None

    @staticmethod
    def _float_or_none(
        value: Any,
    ) -> float | None:
        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None

        return None


def parse_webhook(
    payload: dict[str, Any],
) -> ParsedWebhook:
    """Parse a WhatsApp webhook using the default parser."""

    return WebhookPayloadParser().parse(payload)


__all__ = [
    "ParsedMessage",
    "ParsedMessageType",
    "ParsedWebhook",
    "WebhookPayloadParser",
    "parse_webhook",
]