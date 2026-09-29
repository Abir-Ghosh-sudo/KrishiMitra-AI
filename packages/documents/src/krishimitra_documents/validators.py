from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final


DEFAULT_MAX_FILE_SIZE_BYTES: Final[int] = 20 * 1024 * 1024

ALLOWED_DOCUMENT_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {
        ".pdf",
        ".txt",
        ".csv",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".json",
    }
)

ALLOWED_MIME_TYPES: Final[frozenset[str]] = frozenset(
    {
        "application/pdf",
        "text/plain",
        "text/csv",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/json",
    }
)


class DocumentValidationError(ValueError):
    """Raised when a document fails validation."""


@dataclass(frozen=True, slots=True)
class DocumentValidationResult:
    """Validated document metadata."""

    filename: str
    extension: str
    mime_type: str | None
    size_bytes: int


class DocumentValidator:
    """Validates uploaded agricultural documents before processing."""

    def __init__(
        self,
        *,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
        allowed_extensions: frozenset[str] = ALLOWED_DOCUMENT_EXTENSIONS,
        allowed_mime_types: frozenset[str] = ALLOWED_MIME_TYPES,
    ) -> None:
        if max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be greater than zero")

        self._max_file_size_bytes = max_file_size_bytes
        self._allowed_extensions = frozenset(
            extension.lower() for extension in allowed_extensions
        )
        self._allowed_mime_types = frozenset(
            mime_type.lower() for mime_type in allowed_mime_types
        )

    def validate(
        self,
        *,
        filename: str,
        size_bytes: int,
        mime_type: str | None = None,
    ) -> DocumentValidationResult:
        """Validate document metadata and return normalized information."""
        normalized_filename = self._validate_filename(filename)
        extension = Path(normalized_filename).suffix.lower()

        if extension not in self._allowed_extensions:
            raise DocumentValidationError(
                f"Unsupported document extension: {extension or '<none>'}"
            )

        if size_bytes < 0:
            raise DocumentValidationError("Document size cannot be negative")

        if size_bytes > self._max_file_size_bytes:
            raise DocumentValidationError(
                f"Document exceeds maximum allowed size of "
                f"{self._max_file_size_bytes} bytes"
            )

        normalized_mime_type = self._normalize_mime_type(mime_type)

        if (
            normalized_mime_type is not None
            and normalized_mime_type not in self._allowed_mime_types
        ):
            raise DocumentValidationError(
                f"Unsupported document MIME type: {normalized_mime_type}"
            )

        return DocumentValidationResult(
            filename=normalized_filename,
            extension=extension,
            mime_type=normalized_mime_type,
            size_bytes=size_bytes,
        )

    @staticmethod
    def _validate_filename(filename: str) -> str:
        if not isinstance(filename, str):
            raise DocumentValidationError("Filename must be a string")

        normalized = filename.strip()

        if not normalized:
            raise DocumentValidationError("Filename cannot be empty")

        if len(normalized) > 255:
            raise DocumentValidationError("Filename is too long")

        if "\x00" in normalized:
            raise DocumentValidationError("Filename contains an invalid null byte")

        return Path(normalized).name

    @staticmethod
    def _normalize_mime_type(mime_type: str | None) -> str | None:
        if mime_type is None:
            return None

        normalized = mime_type.strip().lower()

        if not normalized:
            return None

        return normalized


def validate_document(
    *,
    filename: str,
    size_bytes: int,
    mime_type: str | None = None,
) -> DocumentValidationResult:
    """Validate a document using the default production limits."""
    return DocumentValidator().validate(
        filename=filename,
        size_bytes=size_bytes,
        mime_type=mime_type,
    )


__all__ = [
    "ALLOWED_DOCUMENT_EXTENSIONS",
    "ALLOWED_MIME_TYPES",
    "DEFAULT_MAX_FILE_SIZE_BYTES",
    "DocumentValidationError",
    "DocumentValidationResult",
    "DocumentValidator",
    "validate_document",
]