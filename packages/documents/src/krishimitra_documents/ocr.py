from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class OCRProcessingError(RuntimeError):
    """Raised when OCR processing fails."""


@dataclass(frozen=True, slots=True)
class OCRResult:
    """Normalized OCR output."""

    text: str
    language: str | None = None
    confidence: float | None = None


class OCRBackend(Protocol):
    """Backend contract for optical character recognition."""

    def recognize(
        self,
        image: bytes,
        *,
        language: str | None = None,
    ) -> OCRResult:
        """Recognize text from image bytes."""


class OCRProcessor:
    """Coordinates OCR through an injected backend."""

    def __init__(self, backend: OCRBackend) -> None:
        self._backend = backend

    def process(
        self,
        image: bytes | bytearray | memoryview,
        *,
        language: str | None = None,
    ) -> OCRResult:
        if not isinstance(image, (bytes, bytearray, memoryview)):
            raise OCRProcessingError(
                "OCR input must be bytes-like image data"
            )

        payload = bytes(image)

        if not payload:
            raise OCRProcessingError("OCR image is empty")

        normalized_language = self._normalize_language(language)

        try:
            result = self._backend.recognize(
                payload,
                language=normalized_language,
            )
        except OCRProcessingError:
            raise
        except Exception as exc:
            raise OCRProcessingError("OCR processing failed") from exc

        if not isinstance(result, OCRResult):
            raise OCRProcessingError(
                "OCR backend returned an invalid OCRResult"
            )

        normalized_text = self._normalize_text(result.text)

        if not normalized_text:
            raise OCRProcessingError(
                "OCR backend returned no usable text"
            )

        confidence = result.confidence

        if confidence is not None:
            if not 0.0 <= confidence <= 1.0:
                raise OCRProcessingError(
                    "OCR confidence must be between 0 and 1"
                )

        return OCRResult(
            text=normalized_text,
            language=self._normalize_language(result.language),
            confidence=confidence,
        )

    @staticmethod
    def _normalize_language(language: str | None) -> str | None:
        if language is None:
            return None

        if not isinstance(language, str):
            raise OCRProcessingError(
                "OCR language must be a string"
            )

        normalized = language.strip().lower()

        if not normalized:
            return None

        if len(normalized) > 20:
            raise OCRProcessingError(
                "OCR language identifier is too long"
            )

        return normalized

    @staticmethod
    def _normalize_text(text: str) -> str:
        if not isinstance(text, str):
            raise OCRProcessingError(
                "OCR backend returned non-string text"
            )

        lines = (
            line.strip()
            for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        )

        return "\n".join(
            line
            for line in lines
            if line
        ).strip()


def has_usable_ocr_text(result: OCRResult) -> bool:
    """Return whether an OCR result contains usable text."""
    return bool(result.text.strip())


__all__ = [
    "OCRBackend",
    "OCRProcessingError",
    "OCRProcessor",
    "OCRResult",
    "has_usable_ocr_text",
]