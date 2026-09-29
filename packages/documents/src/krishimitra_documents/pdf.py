from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Protocol


class PDFProcessingError(RuntimeError):
    """Raised when PDF processing fails."""


@dataclass(frozen=True, slots=True)
class PDFPage:
    """Text extracted from a single PDF page."""

    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class ParsedPDF:
    """Structured PDF extraction result."""

    filename: str
    pages: tuple[PDFPage, ...]
    text: str
    page_count: int


class PDFBackend(Protocol):
    """Backend contract for PDF text extraction."""

    def extract_pages(self, source: bytes) -> list[str]:
        """Extract text for each PDF page."""


class PDFProcessor:
    """Processes PDFs through an injected extraction backend."""

    def __init__(self, backend: PDFBackend) -> None:
        self._backend = backend

    def process(
        self,
        source: bytes | bytearray | memoryview,
        *,
        filename: str = "document.pdf",
    ) -> ParsedPDF:
        if not isinstance(source, (bytes, bytearray, memoryview)):
            raise PDFProcessingError(
                "PDF source must be bytes-like data"
            )

        payload = bytes(source)

        if not payload:
            raise PDFProcessingError("PDF source is empty")

        if not payload.startswith(b"%PDF-"):
            raise PDFProcessingError("Source does not appear to be a valid PDF")

        normalized_filename = self._normalize_filename(filename)

        try:
            raw_pages = self._backend.extract_pages(payload)
        except PDFProcessingError:
            raise
        except Exception as exc:
            raise PDFProcessingError(
                f"Failed to extract text from PDF: {normalized_filename}"
            ) from exc

        if not isinstance(raw_pages, list):
            raise PDFProcessingError(
                "PDF backend returned an invalid page collection"
            )

        pages: list[PDFPage] = []

        for index, page_text in enumerate(raw_pages, start=1):
            if not isinstance(page_text, str):
                raise PDFProcessingError(
                    f"PDF backend returned invalid text for page {index}"
                )

            normalized_text = self._normalize_text(page_text)

            pages.append(
                PDFPage(
                    page_number=index,
                    text=normalized_text,
                )
            )

        page_count = len(pages)

        if page_count == 0:
            raise PDFProcessingError(
                f"PDF contains no pages: {normalized_filename}"
            )

        combined_text = "\n\n".join(
            page.text
            for page in pages
            if page.text
        ).strip()

        return ParsedPDF(
            filename=normalized_filename,
            pages=tuple(pages),
            text=combined_text,
            page_count=page_count,
        )

    @staticmethod
    def _normalize_filename(filename: str) -> str:
        normalized = filename.strip()

        if not normalized:
            raise PDFProcessingError("PDF filename cannot be empty")

        if "\x00" in normalized:
            raise PDFProcessingError(
                "PDF filename contains an invalid null byte"
            )

        return normalized.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]

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


def is_pdf(source: bytes | bytearray | memoryview) -> bool:
    """Return whether a byte sequence has a PDF file signature."""
    if not isinstance(source, (bytes, bytearray, memoryview)):
        return False

    return bytes(source).startswith(b"%PDF-")


__all__ = [
    "PDFBackend",
    "PDFPage",
    "PDFProcessingError",
    "PDFProcessor",
    "ParsedPDF",
    "is_pdf",
]