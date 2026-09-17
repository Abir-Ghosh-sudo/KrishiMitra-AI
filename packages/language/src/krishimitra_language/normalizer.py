"""Multilingual text normalization primitives for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")
_REPEATED_PUNCTUATION_RE = re.compile(r"([!?.,])\1{2,}")
_ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\uFEFF]")


@dataclass(frozen=True, slots=True)
class NormalizedText:
    """Result of text normalization."""

    original: str
    normalized: str
    changed: bool

    @property
    def is_empty(self) -> bool:
        """Return whether the normalized text is empty."""

        return not self.normalized


def _normalize_unicode(text: str) -> str:
    """Normalize Unicode while preserving the user's script."""

    return unicodedata.normalize("NFC", text)


def _remove_zero_width(text: str) -> str:
    """Remove invisible zero-width formatting characters."""

    return _ZERO_WIDTH_RE.sub("", text)


def _collapse_whitespace(text: str) -> str:
    """Collapse repeated whitespace without altering word content."""

    return _WHITESPACE_RE.sub(" ", text).strip()


def _collapse_punctuation(text: str) -> str:
    """Reduce accidental repeated punctuation."""

    return _REPEATED_PUNCTUATION_RE.sub(r"\1", text)


def normalize_text(text: str) -> NormalizedText:
    """Normalize multilingual user text safely.

    The normalizer intentionally does not transliterate, translate, lowercase
    non-Latin scripts, or remove punctuation that may carry meaning.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    original = text

    normalized = _normalize_unicode(text)
    normalized = _remove_zero_width(normalized)
    normalized = _collapse_whitespace(normalized)
    normalized = _collapse_punctuation(normalized)

    return NormalizedText(
        original=original,
        normalized=normalized,
        changed=normalized != original,
    )


def normalize_for_matching(text: str) -> str:
    """Create a conservative representation for terminology matching."""

    result = normalize_text(text).normalized

    # Case folding is appropriate for matching Latin-script terms while
    # leaving scripts such as Bengali, Hindi, Tamil, etc. intact.
    return result.casefold()


def normalize_for_search(text: str) -> str:
    """Create normalized text suitable for search or RAG queries."""

    result = normalize_for_matching(text)

    # Keep agricultural words and punctuation intact; only remove
    # punctuation that is unlikely to contribute to search semantics.
    result = re.sub(
        r"[^\w\s:/%+\-.]",
        " ",
        result,
        flags=re.UNICODE,
    )

    return _collapse_whitespace(result)


class TextNormalizer:
    """Reusable multilingual text normalization service."""

    def normalize(
        self,
        text: str,
    ) -> NormalizedText:
        """Normalize text while preserving its linguistic identity."""

        return normalize_text(text)

    def for_matching(
        self,
        text: str,
    ) -> str:
        """Normalize text for glossary and terminology matching."""

        return normalize_for_matching(text)

    def for_search(
        self,
        text: str,
    ) -> str:
        """Normalize text for search and RAG retrieval."""

        return normalize_for_search(text)


__all__ = [
    "NormalizedText",
    "TextNormalizer",
    "normalize_for_matching",
    "normalize_for_search",
    "normalize_text",
]