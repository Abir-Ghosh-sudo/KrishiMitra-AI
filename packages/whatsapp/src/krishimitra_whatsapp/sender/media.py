"""WhatsApp media message payload builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MediaSendPayload:
    """Validated payload for sending WhatsApp media."""

    recipient: str
    media_type: str
    media_id: str | None = None
    media_url: str | None = None
    caption: str | None = None
    filename: str | None = None


class MediaPayloadBuilder:
    """Build WhatsApp Cloud API media payloads."""

    _SUPPORTED_TYPES = frozenset(
        {
            "image",
            "audio",
            "video",
            "document",
        }
    )

    def build(
        self,
        *,
        recipient: str,
        media_type: str,
        media_id: str | None = None,
        media_url: str | None = None,
        caption: str | None = None,
        filename: str | None = None,
    ) -> MediaSendPayload:
        normalized_recipient = self._required_string(
            recipient,
            field_name="recipient",
        )
        normalized_type = self._required_string(
            media_type,
            field_name="media_type",
        ).lower()

        if normalized_type not in self._SUPPORTED_TYPES:
            raise ValueError(
                "media_type must be one of: "
                + ", ".join(sorted(self._SUPPORTED_TYPES))
            )

        normalized_media_id = self._optional_string(
            media_id,
            field_name="media_id",
        )
        normalized_media_url = self._optional_string(
            media_url,
            field_name="media_url",
        )

        if normalized_media_id is None and normalized_media_url is None:
            raise ValueError(
                "either media_id or media_url must be provided"
            )

        normalized_caption = self._optional_string(
            caption,
            field_name="caption",
        )
        normalized_filename = self._optional_string(
            filename,
            field_name="filename",
        )

        if normalized_type == "document" and normalized_filename is None:
            raise ValueError("filename is required for document media")

        return MediaSendPayload(
            recipient=normalized_recipient,
            media_type=normalized_type,
            media_id=normalized_media_id,
            media_url=normalized_media_url,
            caption=normalized_caption,
            filename=normalized_filename,
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


def build_media_payload(
    *,
    recipient: str,
    media_type: str,
    media_id: str | None = None,
    media_url: str | None = None,
    caption: str | None = None,
    filename: str | None = None,
) -> dict[str, Any]:
    """Build a WhatsApp Cloud API-compatible media payload."""

    payload = MediaPayloadBuilder().build(
        recipient=recipient,
        media_type=media_type,
        media_id=media_id,
        media_url=media_url,
        caption=caption,
        filename=filename,
    )

    media: dict[str, Any] = {}

    if payload.media_id is not None:
        media["id"] = payload.media_id
    elif payload.media_url is not None:
        media["link"] = payload.media_url

    if payload.caption is not None:
        media["caption"] = payload.caption

    if payload.media_type == "document" and payload.filename is not None:
        media["filename"] = payload.filename

    return {
        "messaging_product": "whatsapp",
        "to": payload.recipient,
        "type": payload.media_type,
        payload.media_type: media,
    }


__all__ = [
    "MediaPayloadBuilder",
    "MediaSendPayload",
    "build_media_payload",
]