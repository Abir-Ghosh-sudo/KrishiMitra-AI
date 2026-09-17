"""WhatsApp media metadata models and extraction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePath


@dataclass(frozen=True, slots=True)
class MediaMetadata:
    """Metadata associated with an incoming WhatsApp media object."""

    media_id: str
    mime_type: str | None = None
    filename: str | None = None
    file_extension: str | None = None
    size_bytes: int | None = None
    caption: str | None = None
    sha256: str | None = None


class MediaMetadataExtractor:
    """Normalize and validate metadata received from WhatsApp."""

    def extract(
        self,
        *,
        media_id: str,
        mime_type: str | None = None,
        filename: str | None = None,
        size_bytes: int | None = None,
        caption: str | None = None,
        sha256: str | None = None,
    ) -> MediaMetadata:
        """Build normalized media metadata."""

        normalized_media_id = self._required_string(
            media_id,
            "media_id",
        )

        normalized_mime_type = self._optional_string(
            mime_type,
        )

        normalized_filename = self._optional_filename(
            filename,
        )

        extension = self._extract_extension(
            normalized_filename,
        )

        if size_bytes is not None and size_bytes < 0:
            raise ValueError(
                "size_bytes must not be negative",
            )

        normalized_caption = self._optional_string(
            caption,
        )

        normalized_sha256 = self._optional_string(
            sha256,
        )

        return MediaMetadata(
            media_id=normalized_media_id,
            mime_type=normalized_mime_type,
            filename=normalized_filename,
            file_extension=extension,
            size_bytes=size_bytes,
            caption=normalized_caption,
            sha256=normalized_sha256,
        )

    @staticmethod
    def _required_string(
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
    def _optional_string(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                "metadata string values must be strings",
            )

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _optional_filename(
        filename: str | None,
    ) -> str | None:
        normalized = MediaMetadataExtractor._optional_string(
            filename,
        )

        if normalized is None:
            return None

        # Prevent path traversal or accidental directory components.
        safe_name = PurePath(normalized).name

        if safe_name in {"", ".", ".."}:
            return None

        return safe_name

    @staticmethod
    def _extract_extension(
        filename: str | None,
    ) -> str | None:
        if not filename:
            return None

        suffix = PurePath(filename).suffix.lower()

        if not suffix:
            return None

        return suffix[1:]


def extract_metadata(
    *,
    media_id: str,
    mime_type: str | None = None,
    filename: str | None = None,
    size_bytes: int | None = None,
    caption: str | None = None,
    sha256: str | None = None,
) -> MediaMetadata:
    """Extract normalized metadata using the default extractor."""

    return MediaMetadataExtractor().extract(
        media_id=media_id,
        mime_type=mime_type,
        filename=filename,
        size_bytes=size_bytes,
        caption=caption,
        sha256=sha256,
    )


__all__ = [
    "MediaMetadata",
    "MediaMetadataExtractor",
    "extract_metadata",
]