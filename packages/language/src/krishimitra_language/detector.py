"""Language detection primitives for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re


class LanguageCode(StrEnum):
    """Supported language codes for agricultural conversations."""

    ENGLISH = "en"
    BENGALI = "bn"
    HINDI = "hi"
    ASSAMESE = "as"
    ODIA = "or"
    PUNJABI = "pa"
    GUJARATI = "gu"
    MARATHI = "mr"
    TELUGU = "te"
    TAMIL = "ta"
    KANNADA = "kn"
    MALAYALAM = "ml"
    URDU = "ur"
    NEPALI = "ne"


class DetectionMethod(StrEnum):
    """Method used to determine the language."""

    EXPLICIT = "explicit"
    SCRIPT = "script"
    HEURISTIC = "heuristic"
    FALLBACK = "fallback"


@dataclass(frozen=True, slots=True)
class LanguageDetection:
    """Result of language detection."""

    language: LanguageCode
    confidence: float
    method: DetectionMethod

    @property
    def is_high_confidence(self) -> bool:
        """Return whether the detection confidence is high."""

        return self.confidence >= 0.85


_SCRIPT_PATTERNS: tuple[
    tuple[LanguageCode, re.Pattern[str]],
    ...
] = (
    (
        LanguageCode.BENGALI,
        re.compile(r"[\u0980-\u09FF]"),
    ),
    (
        LanguageCode.ASSAMESE,
        re.compile(r"[\u0980-\u09FF]"),
    ),
    (
        LanguageCode.ODIA,
        re.compile(r"[\u0B00-\u0B7F]"),
    ),
    (
        LanguageCode.PUNJABI,
        re.compile(r"[\u0A00-\u0A7F]"),
    ),
    (
        LanguageCode.GUJARATI,
        re.compile(r"[\u0A80-\u0AFF]"),
    ),
    (
        LanguageCode.MARATHI,
        re.compile(r"[\u0900-\u097F]"),
    ),
    (
        LanguageCode.HINDI,
        re.compile(r"[\u0900-\u097F]"),
    ),
    (
        LanguageCode.NEPALI,
        re.compile(r"[\u0900-\u097F]"),
    ),
    (
        LanguageCode.TAMIL,
        re.compile(r"[\u0B80-\u0BFF]"),
    ),
    (
        LanguageCode.TELUGU,
        re.compile(r"[\u0C00-\u0C7F]"),
    ),
    (
        LanguageCode.KANNADA,
        re.compile(r"[\u0C80-\u0CFF]"),
    ),
    (
        LanguageCode.MALAYALAM,
        re.compile(r"[\u0D00-\u0D7F]"),
    ),
    (
        LanguageCode.URDU,
        re.compile(r"[\u0600-\u06FF]"),
    ),
)


_SCRIPT_PRIORITY: dict[LanguageCode, tuple[LanguageCode, ...]] = {
    LanguageCode.BENGALI: (
        LanguageCode.BENGALI,
        LanguageCode.ASSAMESE,
    ),
    LanguageCode.HINDI: (
        LanguageCode.HINDI,
        LanguageCode.MARATHI,
        LanguageCode.NEPALI,
    ),
}


def _normalize_text(text: str) -> str:
    """Normalize text for lightweight detection."""

    return " ".join(text.strip().split())


def _script_detection(text: str) -> LanguageDetection | None:
    """Detect languages using Unicode script information."""

    matches: list[LanguageCode] = []

    for language, pattern in _SCRIPT_PATTERNS:
        if pattern.search(text):
            matches.append(language)

    if not matches:
        return None

    if len(matches) == 1:
        return LanguageDetection(
            language=matches[0],
            confidence=0.97,
            method=DetectionMethod.SCRIPT,
        )

    # Shared scripts require a conservative result. More advanced
    # language models can refine this later.
    preferred = matches[0]

    for candidate in matches:
        priority = _SCRIPT_PRIORITY.get(candidate, ())
        if priority and candidate in priority:
            preferred = priority[0]
            break

    return LanguageDetection(
        language=preferred,
        confidence=0.80,
        method=DetectionMethod.SCRIPT,
    )


def _latin_heuristic(text: str) -> LanguageDetection:
    """Apply a lightweight heuristic for Latin-script messages."""

    words = {
        word.lower()
        for word in re.findall(r"[A-Za-z]+", text)
    }

    if not words:
        return LanguageDetection(
            language=LanguageCode.ENGLISH,
            confidence=0.35,
            method=DetectionMethod.FALLBACK,
        )

    # Common agricultural English terms provide a conservative
    # English signal without pretending to replace a real detector.
    english_markers = {
        "the",
        "and",
        "crop",
        "farm",
        "farmer",
        "plant",
        "soil",
        "water",
        "weather",
        "disease",
        "pest",
        "fertilizer",
        "irrigation",
        "rain",
    }

    marker_count = len(words & english_markers)

    if marker_count >= 2:
        return LanguageDetection(
            language=LanguageCode.ENGLISH,
            confidence=0.90,
            method=DetectionMethod.HEURISTIC,
        )

    return LanguageDetection(
        language=LanguageCode.ENGLISH,
        confidence=0.55,
        method=DetectionMethod.HEURISTIC,
    )


class LanguageDetector:
    """Detect the probable language of user-provided text.

    This detector intentionally provides a lightweight deterministic layer.
    Production deployments can place a statistical or neural language
    identification model behind the same interface.
    """

    def __init__(
        self,
        *,
        fallback: LanguageCode = LanguageCode.ENGLISH,
    ) -> None:
        self._fallback = fallback

    def detect(
        self,
        text: str,
        *,
        explicit_language: LanguageCode | None = None,
    ) -> LanguageDetection:
        """Detect a language from text."""

        normalized = _normalize_text(text)

        if explicit_language is not None:
            return LanguageDetection(
                language=explicit_language,
                confidence=1.0,
                method=DetectionMethod.EXPLICIT,
            )

        if not normalized:
            return LanguageDetection(
                language=self._fallback,
                confidence=0.0,
                method=DetectionMethod.FALLBACK,
            )

        script_result = _script_detection(normalized)

        if script_result is not None:
            return script_result

        return _latin_heuristic(normalized)


def detect_language(
    text: str,
    *,
    fallback: LanguageCode = LanguageCode.ENGLISH,
) -> LanguageDetection:
    """Convenience function for language detection."""

    return LanguageDetector(
        fallback=fallback,
    ).detect(text)


__all__ = [
    "DetectionMethod",
    "LanguageCode",
    "LanguageDetection",
    "LanguageDetector",
    "detect_language",
]