"""WhatsApp audio message models for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AudioMessage:
    """Normalized incoming WhatsApp audio message."""

    message_id: str
    sender_id: str
    media_id: str
    mime_type: str | None = None
    sha256: str | None = None
    voice_note: bool = False
    timestamp: str | None = None


class AudioMessageBuilder:
    """Build validated audio message objects."""

    def build(
        self,
        *,
        message_id: str,
        sender_id: str,
        media_id: str,
        mime_type: str | None = None,
        sha256: str | None = None,
        voice_note: bool = False,
        timestamp: str | None = None,
    ) -> AudioMessage:
        """Create a normalized audio message."""

        return AudioMessage(
            message_id=self._required(
                message_id,
                "message_id",
            ),
            sender_id=self._required(
                sender_id,
                "sender_id",
            ),
            media_id=self._required(
                media_id,
                "media_id",
            ),
            mime_type=self._optional(mime_type),
            sha256=self._optional(sha256),
            voice_note=bool(voice_note),
            timestamp=self._optional(timestamp),
        )

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


def build_audio_message(
    *,
    message_id: str,
    sender_id: str,
    media_id: str,
    mime_type: str | None = None,
    sha256: str | None = None,
    voice_note: bool = False,
    timestamp: str | None = None,
) -> AudioMessage:
    """Build an audio message using the default builder."""

    return AudioMessageBuilder().build(
        message_id=message_id,
        sender_id=sender_id,
        media_id=media_id,
        mime_type=mime_type,
        sha256=sha256,
        voice_note=voice_note,
        timestamp=timestamp,
    )


__all__ = [
    "AudioMessage",
    "AudioMessageBuilder",
    "build_audio_message",
]