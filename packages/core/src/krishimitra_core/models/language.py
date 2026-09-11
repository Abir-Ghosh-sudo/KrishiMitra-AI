"""Language models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class LanguageCode(StrEnum):
    """Supported language identifiers."""

    ENGLISH = "en"
    HINDI = "hi"
    BENGALI = "bn"
    ASSAMESE = "as"
    ODIA = "or"
    PUNJABI = "pa"
    GUJARATI = "gu"
    MARATHI = "mr"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MALAYALAM = "ml"
    URDU = "ur"
    NEPALI = "ne"


class LanguageDetection(BaseModel):
    """Detected language information for an incoming message."""

    model_config = ConfigDict(extra="forbid")

    language: LanguageCode
    confidence: float = Field(ge=0.0, le=1.0)
    is_mixed_language: bool = False


class LanguagePreference(BaseModel):
    """Farmer's preferred response language."""

    model_config = ConfigDict(extra="forbid")

    language: LanguageCode
    is_explicit: bool = False


__all__ = [
    "LanguageCode",
    "LanguageDetection",
    "LanguagePreference",
]