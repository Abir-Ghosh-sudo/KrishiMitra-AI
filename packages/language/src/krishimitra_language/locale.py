"""Locale and language preference primitives for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LanguageCode(StrEnum):
    """Supported language codes."""

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


@dataclass(frozen=True, slots=True)
class LanguageLocale:
    """Locale configuration for a language."""

    language: LanguageCode
    locale: str
    display_name: str
    native_name: str
    rtl: bool = False


_LOCALES: dict[LanguageCode, LanguageLocale] = {
    LanguageCode.ENGLISH: LanguageLocale(
        language=LanguageCode.ENGLISH,
        locale="en-IN",
        display_name="English",
        native_name="English",
    ),
    LanguageCode.BENGALI: LanguageLocale(
        language=LanguageCode.BENGALI,
        locale="bn-IN",
        display_name="Bengali",
        native_name="বাংলা",
    ),
    LanguageCode.HINDI: LanguageLocale(
        language=LanguageCode.HINDI,
        locale="hi-IN",
        display_name="Hindi",
        native_name="हिन्दी",
    ),
    LanguageCode.ASSAMESE: LanguageLocale(
        language=LanguageCode.ASSAMESE,
        locale="as-IN",
        display_name="Assamese",
        native_name="অসমীয়া",
    ),
    LanguageCode.ODIA: LanguageLocale(
        language=LanguageCode.ODIA,
        locale="or-IN",
        display_name="Odia",
        native_name="ଓଡ଼ିଆ",
    ),
    LanguageCode.PUNJABI: LanguageLocale(
        language=LanguageCode.PUNJABI,
        locale="pa-IN",
        display_name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
    ),
    LanguageCode.GUJARATI: LanguageLocale(
        language=LanguageCode.GUJARATI,
        locale="gu-IN",
        display_name="Gujarati",
        native_name="ગુજરાતી",
    ),
    LanguageCode.MARATHI: LanguageLocale(
        language=LanguageCode.MARATHI,
        locale="mr-IN",
        display_name="Marathi",
        native_name="मराठी",
    ),
    LanguageCode.TELUGU: LanguageLocale(
        language=LanguageCode.TELUGU,
        locale="te-IN",
        display_name="Telugu",
        native_name="తెలుగు",
    ),
    LanguageCode.TAMIL: LanguageLocale(
        language=LanguageCode.TAMIL,
        locale="ta-IN",
        display_name="Tamil",
        native_name="தமிழ்",
    ),
    LanguageCode.KANNADA: LanguageLocale(
        language=LanguageCode.KANNADA,
        locale="kn-IN",
        display_name="Kannada",
        native_name="ಕನ್ನಡ",
    ),
    LanguageCode.MALAYALAM: LanguageLocale(
        language=LanguageCode.MALAYALAM,
        locale="ml-IN",
        display_name="Malayalam",
        native_name="മലയാളം",
    ),
    LanguageCode.URDU: LanguageLocale(
        language=LanguageCode.URDU,
        locale="ur-IN",
        display_name="Urdu",
        native_name="اردو",
        rtl=True,
    ),
    LanguageCode.NEPALI: LanguageLocale(
        language=LanguageCode.NEPALI,
        locale="ne-IN",
        display_name="Nepali",
        native_name="नेपाली",
    ),
}


class LocaleRegistry:
    """Registry for supported language locales."""

    def __init__(
        self,
        locales: dict[LanguageCode, LanguageLocale] | None = None,
    ) -> None:
        self._locales = dict(
            locales or _LOCALES,
        )

    def get(
        self,
        language: LanguageCode,
    ) -> LanguageLocale | None:
        """Return locale metadata for a language."""

        return self._locales.get(language)

    def require(
        self,
        language: LanguageCode,
    ) -> LanguageLocale:
        """Return locale metadata or raise an error."""

        locale = self.get(language)

        if locale is None:
            raise ValueError(
                f"unsupported language: {language.value}",
            )

        return locale

    def from_locale(
        self,
        locale: str,
    ) -> LanguageLocale | None:
        """Find a language locale by BCP-47-style locale string."""

        normalized = locale.strip().lower()

        for language_locale in self._locales.values():
            if language_locale.locale.lower() == normalized:
                return language_locale

        language_code = normalized.split("-", maxsplit=1)[0]

        try:
            language = LanguageCode(language_code)
        except ValueError:
            return None

        return self.get(language)

    def supported_languages(self) -> tuple[LanguageCode, ...]:
        """Return all supported languages."""

        return tuple(self._locales.keys())

    def __len__(self) -> int:
        """Return the number of supported locales."""

        return len(self._locales)


def get_locale(
    language: LanguageCode,
) -> LanguageLocale:
    """Return locale metadata for a language."""

    return LocaleRegistry().require(language)


__all__ = [
    "LanguageCode",
    "LanguageLocale",
    "LocaleRegistry",
    "get_locale",
]