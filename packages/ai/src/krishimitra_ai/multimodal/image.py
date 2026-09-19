from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ImageInput:
    """Normalized image input for AI vision processing."""

    data: bytes
    mime_type: str
    filename: str | None = None
    media_id: str | None = None
    message_id: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.data:
            raise ValueError("Image data cannot be empty.")

        mime_type = self.mime_type.strip().lower()

        if mime_type not in {
            "image/jpeg",
            "image/png",
            "image/webp",
        }:
            raise ValueError(
                f"Unsupported image MIME type: {self.mime_type}"
            )

        object.__setattr__(self, "mime_type", mime_type)

        if self.filename is not None:
            filename = Path(self.filename).name.strip()

            if not filename:
                raise ValueError("filename cannot be blank.")

            object.__setattr__(self, "filename", filename)

        if self.media_id is not None:
            media_id = self.media_id.strip()

            if not media_id:
                raise ValueError("media_id cannot be blank.")

            object.__setattr__(self, "media_id", media_id)

        if self.message_id is not None:
            message_id = self.message_id.strip()

            if not message_id:
                raise ValueError("message_id cannot be blank.")

            object.__setattr__(self, "message_id", message_id)


@dataclass(frozen=True, slots=True)
class ImageMetadata:
    """Safe metadata associated with an image."""

    width: int | None = None
    height: int | None = None
    file_size_bytes: int | None = None
    format: str | None = None
    source: str | None = None

    def __post_init__(self) -> None:
        if self.width is not None and self.width <= 0:
            raise ValueError("width must be greater than zero.")

        if self.height is not None and self.height <= 0:
            raise ValueError("height must be greater than zero.")

        if (
            self.file_size_bytes is not None
            and self.file_size_bytes < 0
        ):
            raise ValueError("file_size_bytes cannot be negative.")

        if self.format is not None:
            normalized_format = self.format.strip().lower()

            if not normalized_format:
                raise ValueError("format cannot be blank.")

            object.__setattr__(
                self,
                "format",
                normalized_format,
            )

        if self.source is not None:
            normalized_source = self.source.strip()

            if not normalized_source:
                raise ValueError("source cannot be blank.")

            object.__setattr__(
                self,
                "source",
                normalized_source,
            )


@dataclass(frozen=True, slots=True)
class ImageAnalysisInput:
    """Image plus optional agricultural context for vision inference."""

    image: ImageInput
    metadata: ImageMetadata | None = None
    crop: str | None = None
    crop_stage: str | None = None
    location: str | None = None
    user_description: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
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


class ImageProcessor:
    """
    Prepare images for downstream vision models.

    This class deliberately does not perform disease classification.
    Vision inference belongs to the dedicated vision package.
    """

    MAX_IMAGE_SIZE_BYTES = 25 * 1024 * 1024

    SUPPORTED_MIME_TYPES = frozenset(
        {
            "image/jpeg",
            "image/png",
            "image/webp",
        }
    )

    def validate(self, image: ImageInput) -> None:
        """Validate image size and supported format."""

        if len(image.data) > self.MAX_IMAGE_SIZE_BYTES:
            raise ValueError(
                "Image exceeds the maximum supported size of 25 MB."
            )

        if image.mime_type not in self.SUPPORTED_MIME_TYPES:
            raise ValueError(
                f"Unsupported image MIME type: {image.mime_type}"
            )

        self._validate_magic_bytes(image)

    def _validate_magic_bytes(self, image: ImageInput) -> None:
        """Perform lightweight content validation."""

        data = image.data

        if image.mime_type == "image/jpeg":
            if not data.startswith(b"\xff\xd8\xff"):
                raise ValueError(
                    "Image content does not match JPEG format."
                )

        elif image.mime_type == "image/png":
            if not data.startswith(
                b"\x89PNG\r\n\x1a\n"
            ):
                raise ValueError(
                    "Image content does not match PNG format."
                )

        elif image.mime_type == "image/webp":
            if not (
                data.startswith(b"RIFF")
                and len(data) >= 12
                and data[8:12] == b"WEBP"
            ):
                raise ValueError(
                    "Image content does not match WebP format."
                )

    def prepare(
        self,
        image_input: ImageAnalysisInput,
    ) -> ImageAnalysisInput:
        """Validate and return an immutable image input."""

        self.validate(image_input.image)

        return image_input

    @staticmethod
    def build_context(
        image_input: ImageAnalysisInput,
    ) -> dict[str, str]:
        """Build safe contextual information for vision inference."""

        context: dict[str, str] = {}

        values = {
            "crop": image_input.crop,
            "crop_stage": image_input.crop_stage,
            "location": image_input.location,
            "user_description": image_input.user_description,
        }

        for key, value in values.items():
            if value is not None and value.strip():
                context[key] = value.strip()

        if image_input.metadata is not None:
            metadata = image_input.metadata

            if metadata.width is not None:
                context["image_width"] = str(metadata.width)

            if metadata.height is not None:
                context["image_height"] = str(metadata.height)

            if metadata.format is not None:
                context["image_format"] = metadata.format

        return context