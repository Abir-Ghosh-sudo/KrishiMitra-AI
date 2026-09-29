from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class DocumentParseError(RuntimeError):
    """Raised when document parsing fails."""


class DocumentFormat(StrEnum):
    PDF = "pdf"
    TEXT = "text"
    CSV = "csv"
    DOC = "doc"
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"
    JSON = "json"


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    """Structured representation of a parsed document."""

    filename: str
    format: DocumentFormat
    text: str
    page_count: int | None = None
    metadata: dict[str, str] | None = None


class DocumentParserBackend(Protocol):
    """Backend contract for format-specific document parsing."""

    def parse(
        self,
        source: bytes,
        *,
        filename: str,
        document_format: DocumentFormat,
    ) -> ParsedDocument:
        """Parse document bytes into a normalized document."""


class DocumentParser:
    """Routes documents to the appropriate parsing backend."""

    def __init__(self, backend: DocumentParserBackend) -> None:
        self._backend = backend

    def parse(
        self,
        source: bytes | bytearray | memoryview,
        *,
        filename: str,
        document_format: DocumentFormat | str | None = None,
    ) -> ParsedDocument:
        if not isinstance(source, (bytes, bytearray, memoryview)):
            raise DocumentParseError("Document source must be bytes-like data")

        payload = bytes(source)

        if not payload:
            raise DocumentParseError("Document source is empty")

        normalized_filename = filename.strip()

        if not normalized_filename:
            raise DocumentParseError("Filename cannot be empty")

        resolved_format = self._resolve_format(
            filename=normalized_filename,
            document_format=document_format,
        )

        try:
            parsed = self._backend.parse(
                payload,
                filename=normalized_filename,
                document_format=resolved_format,
            )
        except DocumentParseError:
            raise
        except Exception as exc:
            raise DocumentParseError(
                f"Failed to parse document: {normalized_filename}"
            ) from exc

        if not isinstance(parsed, ParsedDocument):
            raise DocumentParseError(
                "Parser backend returned an invalid ParsedDocument"
            )

        if not parsed.text.strip():
            raise DocumentParseError(
                f"Document contains no usable text: {normalized_filename}"
            )

        return ParsedDocument(
            filename=parsed.filename.strip() or normalized_filename,
            format=parsed.format,
            text=parsed.text.strip(),
            page_count=parsed.page_count,
            metadata=dict(parsed.metadata or {}),
        )

    @staticmethod
    def _resolve_format(
        *,
        filename: str,
        document_format: DocumentFormat | str | None,
    ) -> DocumentFormat:
        if document_format is not None:
            if isinstance(document_format, DocumentFormat):
                return document_format

            try:
                return DocumentFormat(str(document_format).lower().strip())
            except ValueError as exc:
                raise DocumentParseError(
                    f"Unsupported document format: {document_format}"
                ) from exc

        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        extension_map = {
            "pdf": DocumentFormat.PDF,
            "txt": DocumentFormat.TEXT,
            "csv": DocumentFormat.CSV,
            "doc": DocumentFormat.DOC,
            "docx": DocumentFormat.DOCX,
            "xls": DocumentFormat.XLS,
            "xlsx": DocumentFormat.XLSX,
            "json": DocumentFormat.JSON,
        }

        resolved = extension_map.get(extension)

        if resolved is None:
            raise DocumentParseError(
                f"Unable to determine document format from filename: {filename}"
            )

        return resolved


__all__ = [
    "DocumentFormat",
    "DocumentParseError",
    "DocumentParser",
    "DocumentParserBackend",
    "ParsedDocument",
]