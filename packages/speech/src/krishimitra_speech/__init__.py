"""Speech processing services for KrishiMitra-AI."""

from .stt import (
    SpeechLanguage,
    SpeechLanguageInfo,
    SpeechToTextBackend,
    TranscriptionResult,
    WhisperTranscriber,
    WhisperTranscriptionError,
    get_language_info,
    is_supported_language,
    supported_languages,
)
from .tts import (
    SpeechSynthesisResult,
    SpeechSynthesizer,
    TextToSpeechBackend,
    TextToSpeechError,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "SpeechLanguage",
    "SpeechLanguageInfo",
    "SpeechSynthesisResult",
    "SpeechSynthesizer",
    "SpeechToTextBackend",
    "TextToSpeechBackend",
    "TextToSpeechError",
    "TranscriptionResult",
    "WhisperTranscriber",
    "WhisperTranscriptionError",
    "get_language_info",
    "is_supported_language",
    "supported_languages",
]