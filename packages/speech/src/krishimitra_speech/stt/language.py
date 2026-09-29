from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SpeechLanguage(StrEnum):
    """Languages supported by the speech pipeline."""

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
class SpeechLanguageInfo:
    """Metadata describing a speech-supported language."""

    code: SpeechLanguage
    name: str
    whisper_code: str


_LANGUAGE_INFO: dict[SpeechLanguage, SpeechLanguageInfo] = {
    SpeechLanguage.ENGLISH: SpeechLanguageInfo(
        code=SpeechLanguage.ENGLISH,
        name="English",
        whisper_code="en",
    ),
    SpeechLanguage.BENGALI: SpeechLanguageInfo(
        code=SpeechLanguage.BENGALI,
        name="Bengali",
        whisper_code="bn",
    ),
    SpeechLanguage.HINDI: SpeechLanguageInfo(
        code=SpeechLanguage.HINDI,
        name="Hindi",
        whisper_code="hi",
    ),
    SpeechLanguage.ASSAMESE: SpeechLanguageInfo(
        code=SpeechLanguage.ASSAMESE,
        name="Assamese",
        whisper_code="as",
    ),
    SpeechLanguage.ODIA: SpeechLanguageInfo(
        code=SpeechLanguage.ODIA,
        name="Odia",
        whisper_code="or",
    ),
    SpeechLanguage.PUNJABI: SpeechLanguageInfo(
        code=SpeechLanguage.PUNJABI,
        name="Punjabi",
        whisper_code="pa",
    ),
    SpeechLanguage.GUJARATI: SpeechLanguageInfo(
        code=SpeechLanguage.GUJARATI,
        name="Gujarati",
        whisper_code="gu",
    ),
    SpeechLanguage.MARATHI: SpeechLanguageInfo(
        code=SpeechLanguage.MARATHI,
        name="Marathi",
        whisper_code="mr",
    ),
    SpeechLanguage.TELUGU: SpeechLanguageInfo(
        code=SpeechLanguage.TELUGU,
        name="Telugu",
        whisper_code="te",
    ),
    SpeechLanguage.TAMIL: SpeechLanguageInfo(
        code=SpeechLanguage.TAMIL,
        name="Tamil",
        whisper_code="ta",
    ),
    SpeechLanguage.KANNADA: SpeechLanguageInfo(
        code=SpeechLanguage.KANNADA,
        name="Kannada",
        whisper_code="kn",
    ),
    SpeechLanguage.MALAYALAM: SpeechLanguageInfo(
        code=SpeechLanguage.MALAYALAM,
        name="Malayalam",
        whisper_code="ml",
    ),
    SpeechLanguage.URDU: SpeechLanguageInfo(
        code=SpeechLanguage.URDU,
        name="Urdu",
        whisper_code="ur",
    ),
    SpeechLanguage.NEPALI: SpeechLanguageInfo(
        code=SpeechLanguage.NEPALI,
        name="Nepali",
        whisper_code="ne",
    ),
}


def get_language_info(language: SpeechLanguage) -> SpeechLanguageInfo:
    """Return metadata for a supported speech language."""

    try:
        return _LANGUAGE_INFO[language]
    except KeyError as exc:
        raise ValueError(f"Unsupported speech language: {language}") from exc


def is_supported_language(language: str | SpeechLanguage) -> bool:
    """Return whether a language code is supported."""

    try:
        SpeechLanguage(language)
    except ValueError:
        return False

    return True


def supported_languages() -> tuple[SpeechLanguage, ...]:
    """Return all supported speech languages."""

    return tuple(_LANGUAGE_INFO)


__all__ = [
    "SpeechLanguage",
    "SpeechLanguageInfo",
    "get_language_info",
    "is_supported_language",
    "supported_languages",
]