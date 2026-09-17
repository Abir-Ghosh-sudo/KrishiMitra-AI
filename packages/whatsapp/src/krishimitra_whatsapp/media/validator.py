"""WhatsApp media validation for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import mimetypes


@dataclass(frozen=True, slots=True)
class MediaValidationResult:
    """Result of validating an incoming media payload."""

    valid: bool
    detected_mime_type: str | None = None
    detected_extension: str | None = None
    size_bytes: int = 0
    sha256: str | None = None
    reason: str | None = None


class MediaValidationError(ValueError):
    """Raised when media validation fails."""


class MediaValidator:
    """Validate media type, size, and basic file signatures."""

    _DEFAULT_ALLOWED_MIME_TYPES = frozenset(
        {
            "image/jpeg",
            "image/png",
            "image/webp",
            "audio/ogg",
            "audio/mpeg",
            "audio/mp4",
            "audio/wav",
            "video/mp4",
            "application/pdf",
            "application/msword",
            (
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
        },
    )

    def __init__(
        self,
        *,
        max_size_bytes: int = 25 * 1024 * 1024,
        allowed_mime_types: frozenset[str] | None = None,
    ) -> None:
        if max_size_bytes <= 0:
            raise ValueError(
                "max_size_bytes must be greater than zero",
            )

        self._max_size_bytes = max_size_bytes
        self._allowed_mime_types = (
            allowed_mime_types
            or self._DEFAULT_ALLOWED_MIME_TYPES
        )

    def validate(
        self,
        *,
        content: bytes,
        declared_mime_type: str | None = None,
        filename: str | None = None,
    ) -> MediaValidationResult:
        """Validate a media payload."""

        if not isinstance(content, bytes):
            raise TypeError("content must be bytes")

        size_bytes = len(content)

        if size_bytes == 0:
            return MediaValidationResult(
                valid=False,
                size_bytes=0,
                reason="empty_media",
            )

        if size_bytes > self._max_size_bytes:
            return MediaValidationResult(
                valid=False,
                size_bytes=size_bytes,
                reason="media_too_large",
            )

        declared = self._normalize_mime_type(
            declared_mime_type,
        )

        if declared is not None:
            if declared not in self._allowed_mime_types:
                return MediaValidationResult(
                    valid=False,
                    size_bytes=size_bytes,
                    reason="unsupported_mime_type",
                )

        detected_mime = self._detect_mime_type(
            content=content,
            filename=filename,
            declared_mime_type=declared,
        )

        if detected_mime is None:
            return MediaValidationResult(
                valid=False,
                size_bytes=size_bytes,
                reason="unable_to_detect_media_type",
            )

        if detected_mime not in self._allowed_mime_types:
            return MediaValidationResult(
                valid=False,
                detected_mime_type=detected_mime,
                size_bytes=size_bytes,
                reason="unsupported_detected_mime_type",
            )

        if (
            declared is not None
            and not self._mime_types_compatible(
                declared,
                detected_mime,
            )
        ):
            return MediaValidationResult(
                valid=False,
                detected_mime_type=detected_mime,
                size_bytes=size_bytes,
                reason="mime_type_mismatch",
            )

        digest = sha256(content).hexdigest()

        return MediaValidationResult(
            valid=True,
            detected_mime_type=detected_mime,
            detected_extension=self._extension_for_mime(
                detected_mime,
            ),
            size_bytes=size_bytes,
            sha256=digest,
        )

    def require_valid(
        self,
        *,
        content: bytes,
        declared_mime_type: str | None = None,
        filename: str | None = None,
    ) -> MediaValidationResult:
        """Validate media or raise MediaValidationError."""

        result = self.validate(
            content=content,
            declared_mime_type=declared_mime_type,
            filename=filename,
        )

        if not result.valid:
            raise MediaValidationError(
                result.reason or "media_validation_failed",
            )

        return result

    def _detect_mime_type(
        self,
        *,
        content: bytes,
        filename: str | None,
        declared_mime_type: str | None,
    ) -> str | None:
        detected = self._detect_by_signature(content)

        if detected is not None:
            return detected

        if filename:
            guessed, _ = mimetypes.guess_type(
                filename,
            )

            if guessed is not None:
                return guessed

        return declared_mime_type

    @staticmethod
    def _detect_by_signature(
        content: bytes,
    ) -> str | None:
        """Detect supported media using file signatures."""

        # JPEG
        if (
            len(content) >= 3
            and content[:3] == b"\xff\xd8\xff"
        ):
            return "image/jpeg"

        # PNG
        if (
            len(content) >= 8
            and content[:8] == b"\x89PNG\r\n\x1a\n"
        ):
            return "image/png"

        # WebP / RIFF container
        if (
            len(content) >= 12
            and content[:4] == b"RIFF"
            and content[8:12] == b"WEBP"
        ):
            return "image/webp"

        # OGG
        if (
            len(content) >= 4
            and content[:4] == b"OggS"
        ):
            return "audio/ogg"

        # PDF
        if content.startswith(b"%PDF-"):
            return "application/pdf"

        # ISO Base Media / MP4
        if (
            len(content) >= 12
            and content[4:8] == b"ftyp"
        ):
            return "video/mp4"

        # WAV / RIFF audio
        if (
            len(content) >= 12
            and content[:4] == b"RIFF"
            and content[8:12] == b"WAVE"
        ):
            return "audio/wav"

        # MP3 with ID3 metadata.
        if content.startswith(b"ID3"):
            return "audio/mpeg"

        # MP3 frame synchronization.
        if (
            len(content) >= 2
            and content[0] == 0xFF
            and (content[1] & 0xE0) == 0xE0
        ):
            return "audio/mpeg"

        return None

    @staticmethod
    def _normalize_mime_type(
        mime_type: str | None,
    ) -> str | None:
        if mime_type is None:
            return None

        normalized = mime_type.strip().lower()

        return normalized or None

    @staticmethod
    def _mime_types_compatible(
        declared: str,
        detected: str,
    ) -> bool:
        if declared == detected:
            return True

        if declared == "audio/mp4" and detected == "audio/mpeg":
            return True

        return False

    @staticmethod
    def _extension_for_mime(
        mime_type: str,
    ) -> str | None:
        mapping = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "audio/ogg": "ogg",
            "audio/mpeg": "mp3",
            "audio/mp4": "m4a",
            "audio/wav": "wav",
            "video/mp4": "mp4",
            "application/pdf": "pdf",
            "application/msword": "doc",
            (
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ): "docx",
        }

        return mapping.get(mime_type)


def validate_media(
    *,
    content: bytes,
    declared_mime_type: str | None = None,
    filename: str | None = None,
    max_size_bytes: int = 25 * 1024 * 1024,
) -> MediaValidationResult:
    """Validate media using the default validator."""

    return MediaValidator(
        max_size_bytes=max_size_bytes,
    ).validate(
        content=content,
        declared_mime_type=declared_mime_type,
        filename=filename,
    )


__all__ = [
    "MediaValidationError",
    "MediaValidationResult",
    "MediaValidator",
    "validate_media",
]