"""Translation primitives for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from krishimitra_language.glossary import AgriculturalGlossary
from krishimitra_language.locale import LanguageCode


class TranslationError(RuntimeError):
    """Raised when a translation operation cannot be completed."""


@dataclass(frozen=True, slots=True)
class TranslationRequest:
    """Request passed to a translation provider."""

    text: str
    source_language: LanguageCode
    target_language: LanguageCode


@dataclass(frozen=True, slots=True)
class TranslationResult:
    """Result returned by a translation provider."""

    source_text: str
    translated_text: str
    source_language: LanguageCode
    target_language: LanguageCode
    provider: str
    confidence: float | None = None


class TranslationProvider(Protocol):
    """Protocol implemented by concrete translation providers."""

    @property
    def name(self) -> str:
        """Return the provider name."""

    def translate(
        self,
        request: TranslationRequest,
    ) -> TranslationResult:
        """Translate a request."""


class GlossaryTranslationProvider:
    """Lightweight translation provider based on the agricultural glossary.

    This provider is intentionally limited to known agricultural terms.
    It does not pretend to be a general-purpose machine translation model.
    """

    def __init__(
        self,
        glossary: AgriculturalGlossary | None = None,
    ) -> None:
        self._glossary = glossary or AgriculturalGlossary()

    @property
    def name(self) -> str:
        """Return the provider name."""

        return "agricultural-glossary"

    def translate(
        self,
        request: TranslationRequest,
    ) -> TranslationResult:
        """Translate a known glossary term."""

        text = request.text.strip()

        if not text:
            raise TranslationError(
                "translation text must not be empty",
            )

        if request.source_language is request.target_language:
            return TranslationResult(
                source_text=text,
                translated_text=text,
                source_language=request.source_language,
                target_language=request.target_language,
                provider=self.name,
                confidence=1.0,
            )

        entry = self._glossary.get(text)

        if entry is None:
            raise TranslationError(
                "no glossary translation available for the requested text",
            )

        translated = entry.translation(
            request.target_language.value,
        )

        if translated == entry.canonical and (
            request.target_language.value
            not in entry.translations
        ):
            raise TranslationError(
                "no translation available for the target language",
            )

        return TranslationResult(
            source_text=text,
            translated_text=translated,
            source_language=request.source_language,
            target_language=request.target_language,
            provider=self.name,
            confidence=0.95,
        )


class Translator:
    """Provider-based translation service."""

    def __init__(
        self,
        providers: tuple[TranslationProvider, ...] | None = None,
    ) -> None:
        self._providers = tuple(
            providers
            or (
                GlossaryTranslationProvider(),
            )
        )

        if not self._providers:
            raise ValueError(
                "at least one translation provider is required",
            )

    def translate(
        self,
        text: str,
        *,
        source_language: LanguageCode,
        target_language: LanguageCode,
    ) -> TranslationResult:
        """Translate text using the configured provider chain."""

        request = TranslationRequest(
            text=text,
            source_language=source_language,
            target_language=target_language,
        )

        errors: list[str] = []

        for provider in self._providers:
            try:
                return provider.translate(request)
            except TranslationError as exc:
                errors.append(
                    f"{provider.name}: {exc}",
                )

        raise TranslationError(
            "translation failed: " + "; ".join(errors),
        )

    def provider_names(self) -> tuple[str, ...]:
        """Return configured provider names."""

        return tuple(
            provider.name
            for provider in self._providers
        )


def translate(
    text: str,
    *,
    source_language: LanguageCode,
    target_language: LanguageCode,
) -> TranslationResult:
    """Convenience function using the default translator."""

    return Translator().translate(
        text,
        source_language=source_language,
        target_language=target_language,
    )


__all__ = [
    "GlossaryTranslationProvider",
    "TranslationError",
    "TranslationProvider",
    "TranslationRequest",
    "TranslationResult",
    "Translator",
    "translate",
]