from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


class MetadataError(ValueError):
    """Raised when RAG metadata is invalid."""


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    """Metadata attached to a knowledge document or chunk."""

    document_id: UUID
    source: str
    title: str | None = None
    language: str | None = None
    document_type: str | None = None
    crop: str | None = None
    disease: str | None = None
    region: str | None = None
    version: str = "1.0"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    extra: dict[str, str] = field(default_factory=dict)


class MetadataBuilder:
    """Builds normalized metadata for RAG ingestion."""

    def build(
        self,
        *,
        source: str,
        title: str | None = None,
        language: str | None = None,
        document_type: str | None = None,
        crop: str | None = None,
        disease: str | None = None,
        region: str | None = None,
        version: str = "1.0",
        document_id: UUID | None = None,
        extra: dict[str, str] | None = None,
    ) -> DocumentMetadata:
        normalized_source = self._required(source, "source")
        normalized_title = self._optional(title)
        normalized_language = self._optional(language)
        normalized_document_type = self._optional(document_type)
        normalized_crop = self._optional(crop)
        normalized_disease = self._optional(disease)
        normalized_region = self._optional(region)
        normalized_version = self._required(version, "version")

        if len(normalized_source) > 500:
            raise MetadataError("source is too long")

        if normalized_title is not None and len(normalized_title) > 500:
            raise MetadataError("title is too long")

        if normalized_language is not None and len(normalized_language) > 20:
            raise MetadataError("language is too long")

        if normalized_document_type is not None and len(normalized_document_type) > 100:
            raise MetadataError("document_type is too long")

        if normalized_crop is not None and len(normalized_crop) > 200:
            raise MetadataError("crop is too long")

        if normalized_disease is not None and len(normalized_disease) > 200:
            raise MetadataError("disease is too long")

        if normalized_region is not None and len(normalized_region) > 200:
            raise MetadataError("region is too long")

        if len(normalized_version) > 50:
            raise MetadataError("version is too long")

        normalized_extra = self._normalize_extra(extra)

        return DocumentMetadata(
            document_id=document_id or uuid4(),
            source=normalized_source,
            title=normalized_title,
            language=normalized_language,
            document_type=normalized_document_type,
            crop=normalized_crop,
            disease=normalized_disease,
            region=normalized_region,
            version=normalized_version,
            extra=normalized_extra,
        )

    @staticmethod
    def _required(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise MetadataError(f"{field_name} must be a string")

        normalized = value.strip()

        if not normalized:
            raise MetadataError(f"{field_name} cannot be empty")

        return normalized

    @staticmethod
    def _optional(value: str | None) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise MetadataError("Metadata values must be strings")

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _normalize_extra(extra: dict[str, str] | None) -> dict[str, str]:
        if extra is None:
            return {}

        if not isinstance(extra, dict):
            raise MetadataError("extra metadata must be a dictionary")

        normalized: dict[str, str] = {}

        for key, value in extra.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise MetadataError(
                    "extra metadata keys and values must be strings"
                )

            normalized_key = key.strip()

            if not normalized_key:
                raise MetadataError(
                    "extra metadata keys cannot be empty"
                )

            normalized[normalized_key] = value.strip()

        return normalized


def build_metadata(
    *,
    source: str,
    title: str | None = None,
    language: str | None = None,
    document_type: str | None = None,
    crop: str | None = None,
    disease: str | None = None,
    region: str | None = None,
    version: str = "1.0",
    document_id: UUID | None = None,
    extra: dict[str, str] | None = None,
) -> DocumentMetadata:
    """Convenience wrapper around MetadataBuilder."""
    return MetadataBuilder().build(
        source=source,
        title=title,
        language=language,
        document_type=document_type,
        crop=crop,
        disease=disease,
        region=region,
        version=version,
        document_id=document_id,
        extra=extra,
    )


__all__ = [
    "DocumentMetadata",
    "MetadataBuilder",
    "MetadataError",
    "build_metadata",
]