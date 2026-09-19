from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class DocumentInput:
    """Normalized agricultural document input."""

    data: bytes
    mime_type: str
    filename: str | None = None
    media_id: str | None = None
    message_id: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.data:
            raise ValueError("Document data cannot be empty.")

        mime_type = self.mime_type.strip().lower()

        allowed_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        }

        if mime_type not in allowed_types:
            raise ValueError(
                f"Unsupported document MIME type: {self.mime_type}"
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


@dataclass(frozen=True, slots=True)
class DocumentAnalysisInput:
    """Document plus optional agricultural context."""

    document: DocumentInput
    document_type: str | None = None
    crop: str | None = None
    crop_stage: str | None = None
    location: str | None = None
    user_description: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "document_type",
            "crop",
            "crop_stage",
            "location",
            "user_description",
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


@dataclass(frozen=True, slots=True)
class DocumentText:
    """Extracted text produced by the document pipeline."""

    text: str
    page_count: int | None = None
    language: str | None = None

    def __post_init__(self) -> None:
        text = self.text.strip()

        if not text:
            raise ValueError(
                "Extracted document text cannot be empty."
            )

        object.__setattr__(self, "text", text)

        if self.page_count is not None and self.page_count <= 0:
            raise ValueError(
                "page_count must be greater than zero."
            )

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


class DocumentProcessor:
    """
    Prepare agricultural documents for downstream document/RAG processing.

    This class validates the input container only. PDF/DOCX extraction,
    OCR, chunking, embedding, and retrieval belong to their dedicated
    packages.
    """

    MAX_DOCUMENT_SIZE_BYTES = 25 * 1024 * 1024

    SUPPORTED_MIME_TYPES = frozenset(
        {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        }
    )

    def validate(self, document: DocumentInput) -> None:
        """Validate document size, MIME type, and basic file signature."""

        if len(document.data) > self.MAX_DOCUMENT_SIZE_BYTES:
            raise ValueError(
                "Document exceeds the maximum supported size of 25 MB."
            )

        if document.mime_type not in self.SUPPORTED_MIME_TYPES:
            raise ValueError(
                f"Unsupported document MIME type: {document.mime_type}"
            )

        self._validate_magic_bytes(document)

    def _validate_magic_bytes(
        self,
        document: DocumentInput,
    ) -> None:
        """Perform lightweight container validation."""

        data = document.data
        mime_type = document.mime_type

        if mime_type == "application/pdf":
            if not data.startswith(b"%PDF-"):
                raise ValueError(
                    "Document content does not match PDF format."
                )

        elif mime_type == "application/msword":
            if not data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
                raise ValueError(
                    "Document content does not match legacy DOC format."
                )

        elif mime_type == (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            if not data.startswith(b"PK"):
                raise ValueError(
                    "Document content does not match DOCX format."
                )

        elif mime_type == "text/plain":
            self._validate_text_content(data)

    @staticmethod
    def _validate_text_content(data: bytes) -> None:
        """Ensure a text document can be decoded safely."""

        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            try:
                data.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise ValueError(
                    "Text document is not valid UTF-8."
                ) from exc

    def prepare(
        self,
        document_input: DocumentAnalysisInput,
    ) -> DocumentAnalysisInput:
        """Validate and return the normalized document input."""

        self.validate(document_input.document)

        return document_input

    @staticmethod
    def build_context(
        document_input: DocumentAnalysisInput,
    ) -> dict[str, str]:
        """Build safe context for document intelligence."""

        context: dict[str, str] = {}

        values = {
            "document_type": document_input.document_type,
            "crop": document_input.crop,
            "crop_stage": document_input.crop_stage,
            "location": document_input.location,
            "user_description": document_input.user_description,
        }

        for key, value in values.items():
            if value is not None and value.strip():
                context[key] = value.strip()

        if document_input.document.filename is not None:
            context["filename"] = (
                document_input.document.filename
            )

        context["mime_type"] = (
            document_input.document.mime_type
        )

        return context