"""Text-to-speech services for KrishiMitra-AI."""

from .engine import (
    SpeechSynthesisResult,
    SpeechSynthesizer,
    TextToSpeechBackend,
    TextToSpeechError,
)

__all__ = [
    "SpeechSynthesisResult",
    "SpeechSynthesizer",
    "TextToSpeechBackend",
    "TextToSpeechError",
]