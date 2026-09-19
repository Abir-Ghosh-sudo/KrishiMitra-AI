from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class VoiceInput:
    """Normalized voice/audio input for speech processing."""

    data: bytes
    mime_type: str
    filename: str | None = None
    media_id: str | None = None
    message_id: str | None = None
    duration_seconds: float | None = None
    language_hint: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.data:
            raise ValueError("Voice data cannot be empty.")

        mime_type = self.mime_type.strip().lower()

        allowed_types = {
            "audio/ogg",
            "audio/mpeg",
            "audio/mp3",
            "audio/wav",
            "audio/x-wav",
            "audio/mp4",
            "audio/aac",
            "audio/webm",
        }

        if mime_type not in allowed_types:
            raise ValueError(
                f"Unsupported audio MIME type: {self.mime_type}"
            )

        object.__setattr__(self, "mime_type", mime_type)

        if self.filename is not None:
            filename = Path(self.filename).name.strip()

            if not filename:
                raise ValueError("filename cannot be blank.")

            object.__setattr__(
                self,
                "filename",
                filename,
            )

        if self.media_id is not None:
            media_id = self.media_id.strip()

            if not media_id:
                raise ValueError("media_id cannot be blank.")

            object.__setattr__(
                self,
                "media_id",
                media_id,
            )

        if self.message_id is not None:
            message_id = self.message_id.strip()

            if not message_id:
                raise ValueError("message_id cannot be blank.")

            object.__setattr__(
                self,
                "message_id",
                message_id,
            )

        if self.duration_seconds is not None:
            if self.duration_seconds <= 0:
                raise ValueError(
                    "duration_seconds must be greater than zero."
                )

        if self.language_hint is not None:
            language_hint = self.language_hint.strip().lower()

            if not language_hint:
                raise ValueError(
                    "language_hint cannot be blank."
                )

            object.__setattr__(
                self,
                "language_hint",
                language_hint,
            )


@dataclass(frozen=True, slots=True)
class Transcription:
    """Speech-to-text result passed into the AI layer."""

    text: str
    language: str | None = None
    confidence: float | None = None
    duration_seconds: float | None = None
    segments: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        text = self.text.strip()

        if not text:
            raise ValueError("Transcription text cannot be empty.")

        object.__setattr__(self, "text", text)

        if self.language is not None:
            language = self.language.strip().lower()

            if not language:
                raise ValueError(
                    "language cannot be blank."
                )

            object.__setattr__(
                self,
                "language",
                language,
            )

        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "confidence must be between 0.0 and 1.0."
                )

        if self.duration_seconds is not None:
            if self.duration_seconds <= 0:
                raise ValueError(
                    "duration_seconds must be greater than zero."
                )

        normalized_segments = tuple(
            segment.strip()
            for segment in self.segments
            if segment.strip()
        )

        object.__setattr__(
            self,
            "segments",
            normalized_segments,
        )


@dataclass(frozen=True, slots=True)
class VoiceAnalysisInput:
    """Voice input plus optional agricultural context."""

    voice: VoiceInput
    transcription: Transcription | None = None
    user_description: str | None = None
    crop: str | None = None
    crop_stage: str | None = None
    location: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "user_description",
            "crop",
            "crop_stage",
            "location",
        ):
            value = getattr(self, field_name)

            if value is not None:
                normalized = value.strip()

                if not normalized:
                    raise ValueError(
                        f"{field_name} cannot be blank."
                    )

                object.__setattr__(
                    self,
                    field_name,
                    normalized,
                )


class VoiceProcessor:
    """
    Prepare voice messages for the speech pipeline.

    Actual speech-to-text belongs to the dedicated speech package.
    This layer only validates and normalizes the multimodal input.
    """

    MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024

    SUPPORTED_MIME_TYPES = frozenset(
        {
            "audio/ogg",
            "audio/mpeg",
            "audio/mp3",
            "audio/wav",
            "audio/x-wav",
            "audio/mp4",
            "audio/aac",
            "audio/webm",
        }
    )

    def validate(self, voice: VoiceInput) -> None:
        """Validate audio size and MIME type."""

        if len(voice.data) > self.MAX_AUDIO_SIZE_BYTES:
            raise ValueError(
                "Audio exceeds the maximum supported size of 25 MB."
            )

        if voice.mime_type not in self.SUPPORTED_MIME_TYPES:
            raise ValueError(
                f"Unsupported audio MIME type: {voice.mime_type}"
            )

        self._validate_magic_bytes(voice)

    def _validate_magic_bytes(
        self,
        voice: VoiceInput,
    ) -> None:
        """Perform lightweight audio container validation."""

        data = voice.data
        mime_type = voice.mime_type

        if mime_type == "audio/ogg":
            if not data.startswith(b"OggS"):
                raise ValueError(
                    "Audio content does not match OGG format."
                )

        elif mime_type in {
            "audio/wav",
            "audio/x-wav",
        }:
            if not (
                data.startswith(b"RIFF")
                and len(data) >= 12
                and data[8:12] == b"WAVE"
            ):
                raise ValueError(
                    "Audio content does not match WAV format."
                )

        elif mime_type in {
            "audio/mpeg",
            "audio/mp3",
        }:
            has_id3_header = data.startswith(b"ID3")

            has_mpeg_frame = (
                len(data) >= 2
                and data[0] == 0xFF
                and (data[1] & 0xE0) == 0xE0
            )

            if not (has_id3_header or has_mpeg_frame):
                raise ValueError(
                    "Audio content does not match MPEG audio format."
                )

        elif mime_type == "audio/mp4":
            if len(data) < 12 or data[4:8] != b"ftyp":
                raise ValueError(
                    "Audio content does not match MP4 container format."
                )

    def prepare(
        self,
        voice_input: VoiceAnalysisInput,
    ) -> VoiceAnalysisInput:
        """Validate and return normalized voice input."""

        self.validate(voice_input.voice)

        return voice_input

    @staticmethod
    def build_context(
        voice_input: VoiceAnalysisInput,
    ) -> dict[str, str]:
        """Build safe context for downstream speech/AI processing."""

        context: dict[str, str] = {}

        values = {
            "crop": voice_input.crop,
            "crop_stage": voice_input.crop_stage,
            "location": voice_input.location,
            "user_description": voice_input.user_description,
        }

        for key, value in values.items():
            if value is not None and value.strip():
                context[key] = value.strip()

        transcription = voice_input.transcription

        if transcription is not None:
            context["transcription"] = transcription.text

            if transcription.language is not None:
                context["transcription_language"] = (
                    transcription.language
                )

            if transcription.confidence is not None:
                context["transcription_confidence"] = (
                    f"{transcription.confidence:.3f}"
                )

        if voice_input.voice.language_hint is not None:
            context["language_hint"] = (
                voice_input.voice.language_hint
            )

        return context