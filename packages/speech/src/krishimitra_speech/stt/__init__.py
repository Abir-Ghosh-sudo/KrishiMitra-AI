"""Speech-to-text services for KrishiMitra-AI."""

from .language import (
    SpeechLanguage,
    SpeechLanguageInfo,
    get_language_info,
    is_supported_language,
    supported_languages,
)
from .whisper import (
    SpeechToTextBackend,
    TranscriptionResult,
    WhisperTranscriber,
    WhisperTranscriptionError,
)

__all__ = [
    "SpeechLanguage",
    "SpeechLanguageInfo",
    "SpeechToTextBackend",
    "TranscriptionResult",
    "WhisperTranscriber",
    "WhisperTranscriptionError",
    "get_language_info",
    "is_supported_language",
    "supported_languages",
]