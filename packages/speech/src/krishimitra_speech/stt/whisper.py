from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .language import SpeechLanguage, get_language_info


class SpeechToTextBackend(Protocol):
    """Protocol for an actual speech-to-text model backend."""

    def transcribe(
        self,
        audio_path: str | Path,
        *,
        language: str | None = None,
    ) -> tuple[str, str | None, float | None]:
        ...


@dataclass(frozen=True, slots=True)
class TranscriptionResult:
    """Result returned by the speech-to-text service."""

    text: str
    language: SpeechLanguage | None
    confidence: float | None
    model: str
    duration_seconds: float | None = None


class WhisperTranscriptionError(RuntimeError):
    """Raised when speech transcription cannot be completed."""


class WhisperTranscriber:
    """
    Speech-to-text service backed by an injected Whisper-compatible backend.

    The model is intentionally injected instead of loaded at import time.
    This keeps the package lightweight and allows local Whisper,
    faster-whisper, or another compatible backend to be used in production.
    """

    def __init__(
        self,
        backend: SpeechToTextBackend,
        *,
        model_name: str = "whisper",
    ) -> None:
        self._backend = backend
        self._model_name = model_name

    def transcribe(
        self,
        audio_path: str | Path,
        *,
        language: SpeechLanguage | str | None = None,
    ) -> TranscriptionResult:
        path = Path(audio_path)

        if not path.is_file():
            raise WhisperTranscriptionError(
                f"Audio file does not exist: {path}"
            )

        language_code: str | None = None
        normalized_language: SpeechLanguage | None = None

        if language is not None:
            try:
                normalized_language = SpeechLanguage(language)
            except ValueError as exc:
                raise WhisperTranscriptionError(
                    f"Unsupported speech language: {language}"
                ) from exc

            language_code = get_language_info(
                normalized_language
            ).whisper_code

        try:
            text, detected_language, confidence = self._backend.transcribe(
                path,
                language=language_code,
            )
        except Exception as exc:
            raise WhisperTranscriptionError(
                f"Speech transcription failed for: {path}"
            ) from exc

        cleaned_text = text.strip()

        if not cleaned_text:
            raise WhisperTranscriptionError(
                "Speech transcription returned empty text."
            )

        detected_enum: SpeechLanguage | None = normalized_language

        if detected_language:
            try:
                detected_enum = SpeechLanguage(detected_language)
            except ValueError:
                detected_enum = normalized_language

        return TranscriptionResult(
            text=cleaned_text,
            language=detected_enum,
            confidence=confidence,
            model=self._model_name,
        )


__all__ = [
    "SpeechToTextBackend",
    "TranscriptionResult",
    "WhisperTranscriptionError",
    "WhisperTranscriber",
]