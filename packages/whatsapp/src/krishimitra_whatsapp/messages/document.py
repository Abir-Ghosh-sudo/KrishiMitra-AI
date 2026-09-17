"""WhatsApp document message models for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DocumentMessage:
    """Normalized incoming WhatsApp document message."""

    message_id: str
    sender_id: str
    media_id: str
    filename: str | None = None
    mime_type: str | None = None
    sha256: str | None = None
    caption: str | None = None
    timestamp: str | None = None


class DocumentMessageBuilder:
    """Build validated document message objects."""

    def build(
        self,
        *,
        message_id: str,
        sender_id: str,
        media_id: str,
        filename: str | None = None,
        mime_type: str | None = None,
        sha256: str | None = None,
        caption: str | None = None,
        timestamp: str | None = None,
    ) -> DocumentMessage:
        """Create a normalized document message."""

        return DocumentMessage(
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
            filename=self._optional(filename),
            mime_type=self._optional(mime_type),
            sha256=self._optional(sha256),
            caption=self._optional(caption),
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


def build_document_message(
    *,
    message_id: str,
    sender_id: str,
    media_id: str,
    filename: str | None = None,
    mime_type: str | None = None,
    sha256: str | None = None,
    caption: str | None = None,
    timestamp: str | None = None,
) -> DocumentMessage:
    """Build a document message using the default builder."""

    return DocumentMessageBuilder().build(
        message_id=message_id,
        sender_id=sender_id,
        media_id=media_id,
        filename=filename,
        mime_type=mime_type,
        sha256=sha256,
        caption=caption,
        timestamp=timestamp,
    )


__all__ = [
    "DocumentMessage",
    "DocumentMessageBuilder",
    "build_document_message",
]