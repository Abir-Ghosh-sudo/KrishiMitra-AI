from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..stt.language import SpeechLanguage


class TextToSpeechBackend(Protocol):
    """Protocol for an actual text-to-speech backend."""

    def synthesize(
        self,
        text: str,
        *,
        language: str,
        output_path: str | Path,
    ) -> None:
        ...


@dataclass(frozen=True, slots=True)
class SpeechSynthesisResult:
    """Result returned after speech synthesis."""

    output_path: Path
    language: SpeechLanguage
    text_length: int
    engine: str


class TextToSpeechError(RuntimeError):
    """Raised when text-to-speech synthesis fails."""


class SpeechSynthesizer:
    """
    Text-to-speech service using an injected backend.

    Backend implementations may use a local/open-source TTS engine
    without coupling the core speech package to a specific runtime.
    """

    def __init__(
        self,
        backend: TextToSpeechBackend,
        *,
        engine_name: str = "tts",
    ) -> None:
        self._backend = backend
        self._engine_name = engine_name

    def synthesize(
        self,
        text: str,
        *,
        language: SpeechLanguage | str,
        output_path: str | Path,
    ) -> SpeechSynthesisResult:
        cleaned_text = text.strip()

        if not cleaned_text:
            raise TextToSpeechError(
                "Text-to-speech input cannot be empty."
            )

        try:
            normalized_language = SpeechLanguage(language)
        except ValueError as exc:
            raise TextToSpeechError(
                f"Unsupported speech language: {language}"
            ) from exc

        destination = Path(output_path)

        if destination.suffix == "":
            raise TextToSpeechError(
                "Output path must include a file extension."
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            self._backend.synthesize(
                cleaned_text,
                language=normalized_language.value,
                output_path=destination,
            )
        except Exception as exc:
            raise TextToSpeechError(
                "Text-to-speech synthesis failed."
            ) from exc

        if not destination.is_file():
            raise TextToSpeechError(
                f"TTS backend did not create output file: {destination}"
            )

        return SpeechSynthesisResult(
            output_path=destination,
            language=normalized_language,
            text_length=len(cleaned_text),
            engine=self._engine_name,
        )


__all__ = [
    "TextToSpeechBackend",
    "SpeechSynthesisResult",
    "TextToSpeechError",
    "SpeechSynthesizer",
]