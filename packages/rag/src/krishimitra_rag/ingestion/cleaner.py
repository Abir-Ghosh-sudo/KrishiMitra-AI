from __future__ import annotations

import re
import unicodedata


class TextCleaningError(ValueError):
    """Raised when document text cannot be cleaned."""


class TextCleaner:
    """Normalizes extracted agricultural knowledge before chunking."""

    _MULTIPLE_SPACES = re.compile(r"[ \t]+")
    _MULTIPLE_NEWLINES = re.compile(r"\n{3,}")

    def clean(self, text: str) -> str:
        """Return normalized text while preserving meaningful structure."""
        if not isinstance(text, str):
            raise TextCleaningError("Text must be a string")

        if not text.strip():
            raise TextCleaningError("Text cannot be empty")

        normalized = unicodedata.normalize("NFKC", text)

        normalized = normalized.replace("\r\n", "\n")
        normalized = normalized.replace("\r", "\n")

        lines = [
            self._clean_line(line)
            for line in normalized.split("\n")
        ]

        normalized = "\n".join(lines)
        normalized = self._MULTIPLE_NEWLINES.sub("\n\n", normalized)

        normalized = normalized.strip()

        if not normalized:
            raise TextCleaningError("Text contains no usable content")

        return normalized

    @classmethod
    def _clean_line(cls, line: str) -> str:
        line = line.replace("\u00a0", " ")
        line = cls._MULTIPLE_SPACES.sub(" ", line)
        return line.strip()


def clean_text(text: str) -> str:
    """Convenience wrapper around TextCleaner."""
    return TextCleaner().clean(text)


__all__ = [
    "TextCleaner",
    "TextCleaningError",
    "clean_text",
]