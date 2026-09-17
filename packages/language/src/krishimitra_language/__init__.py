"""Multilingual language services for KrishiMitra-AI."""

from __future__ import annotations

from krishimitra_language.detector import (
    DetectionMethod,
    LanguageCode as DetectedLanguageCode,
    LanguageDetection,
    LanguageDetector,
    detect_language,
)
from krishimitra_language.glossary import (
    AgriculturalGlossary,
    GlossaryCategory,
    GlossaryEntry,
    get_glossary,
)
from krishimitra_language.locale import (
    LanguageCode,
    LanguageLocale,
    LocaleRegistry,
    get_locale,
)
from krishimitra_language.normalizer import (
    NormalizedText,
    TextNormalizer,
    normalize_for_matching,
    normalize_for_search,
    normalize_text,
)
from krishimitra_language.translator import (
    GlossaryTranslationProvider,
    TranslationError,
    TranslationProvider,
    TranslationRequest,
    TranslationResult,
    Translator,
    translate,
)

__all__ = [
    "AgriculturalGlossary",
    "DetectedLanguageCode",
    "DetectionMethod",
    "GlossaryCategory",
    "GlossaryEntry",
    "GlossaryTranslationProvider",
    "LanguageCode",
    "LanguageDetection",
    "LanguageDetector",
    "LanguageLocale",
    "LocaleRegistry",
    "NormalizedText",
    "TextNormalizer",
    "TranslationError",
    "TranslationProvider",
    "TranslationRequest",
    "TranslationResult",
    "Translator",
    "detect_language",
    "get_glossary",
    "get_locale",
    "normalize_for_matching",
    "normalize_for_search",
    "normalize_text",
    "translate",
]