from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class DocumentExtractionError(RuntimeError):
    """Raised when document text extraction fails."""


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    """Normalized text extracted from a document."""

    source_name: str
    text: str
    page_count: int | None = None
    character_count: int = 0


class DocumentExtractorBackend(Protocol):
    """Backend contract for document text extraction."""

    def extract(
        self,
        source: bytes,
        *,
        filename: str,
    ) -> tuple[str, int | None]:
        """Extract text and optional page count from document bytes."""


class DocumentExtractor:
    """Coordinates document extraction through an injected backend."""

    def __init__(self, backend: DocumentExtractorBackend) -> None:
        self._backend = backend

    def extract(
        self,
        source: bytes | bytearray | memoryview,
        *,
        filename: str,
    ) -> ExtractedDocument:
        if not isinstance(source, (bytes, bytearray, memoryview)):
            raise DocumentExtractionError(
                "Document source must be bytes-like data"
            )

        normalized_filename = self._normalize_filename(filename)

        payload = bytes(source)

        if not payload:
            raise DocumentExtractionError("Document source is empty")

        try:
            text, page_count = self._backend.extract(
                payload,
                filename=normalized_filename,
            )
        except DocumentExtractionError:
            raise
        except Exception as exc:
            raise DocumentExtractionError(
                f"Document extraction failed for {normalized_filename}"
            ) from exc

        if not isinstance(text, str):
            raise DocumentExtractionError(
                "Document extraction backend returned invalid text"
            )

        normalized_text = self._normalize_text(text)

        if not normalized_text:
            raise DocumentExtractionError(
                f"No extractable text found in {normalized_filename}"
            )

        if page_count is not None:
            if not isinstance(page_count, int) or page_count <= 0:
                raise DocumentExtractionError(
                    "Document extraction backend returned invalid page count"
                )

        return ExtractedDocument(
            source_name=normalized_filename,
            text=normalized_text,
            page_count=page_count,
            character_count=len(normalized_text),
        )

    @staticmethod
    def _normalize_filename(filename: str) -> str:
        if not isinstance(filename, str):
            raise DocumentExtractionError("Filename must be a string")

        normalized = filename.strip()

        if not normalized:
            raise DocumentExtractionError("Filename cannot be empty")

        if "\x00" in normalized:
            raise DocumentExtractionError(
                "Filename contains an invalid null byte"
            )

        return Path(normalized).name

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = (
            line.strip()
            for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        )

        return "\n".join(
            line
            for line in lines
            if line
        ).strip()


__all__ = [
    "DocumentExtractionError",
    "DocumentExtractor",
    "DocumentExtractorBackend",
    "ExtractedDocument",
]