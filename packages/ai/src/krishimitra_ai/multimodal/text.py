from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from krishimitra_language import detect_language

from ..llm.base import LLMMessage
from ..llm.prompts import build_user_prompt


@dataclass(frozen=True, slots=True)
class TextInput:
    """Normalized text input received by the AI layer."""

    text: str
    language: str | None = None
    sender_id: str | None = None
    message_id: str | None = None
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        text = self.text.strip()

        if not text:
            raise ValueError("Text input cannot be empty.")

        object.__setattr__(self, "text", text)

        if self.language is not None:
            language = self.language.strip().lower()

            if not language:
                raise ValueError("language cannot be blank.")

            object.__setattr__(self, "language", language)

        if self.sender_id is not None:
            sender_id = self.sender_id.strip()

            if not sender_id:
                raise ValueError("sender_id cannot be blank.")

            object.__setattr__(self, "sender_id", sender_id)

        if self.message_id is not None:
            message_id = self.message_id.strip()

            if not message_id:
                raise ValueError("message_id cannot be blank.")

            object.__setattr__(self, "message_id", message_id)


@dataclass(frozen=True, slots=True)
class TextAnalysis:
    """Language and normalization information extracted from text."""

    original_text: str
    normalized_text: str
    detected_language: str | None
    language_confidence: float | None

    def __post_init__(self) -> None:
        if not self.original_text.strip():
            raise ValueError("original_text cannot be empty.")

        if not self.normalized_text.strip():
            raise ValueError("normalized_text cannot be empty.")

        if self.language_confidence is not None:
            if not 0.0 <= self.language_confidence <= 1.0:
                raise ValueError(
                    "language_confidence must be between 0.0 and 1.0."
                )


class TextProcessor:
    """Prepare farmer text for downstream AI orchestration."""

    def analyze(self, text_input: TextInput) -> TextAnalysis:
        """Normalize text and detect its language."""

        original_text = text_input.text
        normalized_text = self.normalize(original_text)

        detected_language: str | None = text_input.language
        confidence: float | None = None

        if detected_language is None:
            detection = self.detect_language(normalized_text)

            if detection is not None:
                detected_language, confidence = detection

        return TextAnalysis(
            original_text=original_text,
            normalized_text=normalized_text,
            detected_language=detected_language,
            language_confidence=confidence,
        )

    @staticmethod
    def normalize(text: str) -> str:
        """Apply conservative text normalization."""

        normalized = " ".join(text.strip().split())

        if not normalized:
            raise ValueError("Text cannot be empty after normalization.")

        return normalized

    @staticmethod
    def detect_language(
        text: str,
    ) -> tuple[str, float | None] | None:
        """
        Detect language using the shared KrishiMitra language package.

        The language package intentionally owns language-detection policy;
        this processor only adapts its result for the AI layer.
        """

        normalized = text.strip()

        if not normalized:
            return None

        try:
            result = detect_language(normalized)
        except (ValueError, TypeError):
            return None

        if result is None:
            return None

        language = getattr(result, "language", None)

        if language is None:
            language = getattr(result, "code", None)

        if language is None:
            return None

        language_value = getattr(language, "value", language)
        language_value = str(language_value).strip().lower()

        if not language_value:
            return None

        confidence = getattr(result, "confidence", None)

        if isinstance(confidence, (int, float)):
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))
        else:
            confidence = None

        return language_value, confidence

    def to_llm_message(
        self,
        text_input: TextInput,
        *,
        context: Mapping[str, object] | None = None,
    ) -> LLMMessage:
        """Convert farmer text into an LLM-ready user message."""

        prompt = build_user_prompt(
            user_message=text_input.text,
            context=context,
        )

        return LLMMessage(
            role="user",
            content=prompt,
        )