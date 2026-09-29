from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


class ImagePreprocessingError(ValueError):
    """Raised when an image cannot be safely preprocessed."""


@dataclass(frozen=True, slots=True)
class PreprocessedImage:
    """Normalized image representation used by vision models."""

    image: np.ndarray
    width: int
    height: int
    channels: int
    source_format: str | None


class ImagePreprocessor:
    """Validate and normalize agricultural images for inference."""

    def __init__(
        self,
        *,
        target_size: tuple[int, int] = (224, 224),
        normalize: bool = True,
    ) -> None:
        width, height = target_size

        if width <= 0 or height <= 0:
            raise ValueError("target_size dimensions must be positive")

        self._target_size = (width, height)
        self._normalize = normalize

    def process(
        self,
        source: str | Path | bytes | bytearray | np.ndarray | Image.Image,
    ) -> PreprocessedImage:
        image, source_format = self._load(source)

        if image.size == 0:
            raise ImagePreprocessingError("Image is empty")

        rgb = self._to_rgb(image)

        width, height = self._target_size
        resized = cv2.resize(
            rgb,
            (width, height),
            interpolation=cv2.INTER_AREA,
        )

        processed = resized.astype(np.float32)

        if self._normalize:
            processed /= 255.0

        return PreprocessedImage(
            image=processed,
            width=width,
            height=height,
            channels=3,
            source_format=source_format,
        )

    def _load(
        self,
        source: str | Path | bytes | bytearray | np.ndarray | Image.Image,
    ) -> tuple[np.ndarray, str | None]:
        if isinstance(source, Image.Image):
            return np.asarray(source), source.format

        if isinstance(source, np.ndarray):
            return source, None

        if isinstance(source, (bytes, bytearray)):
            data = np.frombuffer(source, dtype=np.uint8)
            image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)

            if image is None:
                raise ImagePreprocessingError(
                    "Unable to decode image bytes"
                )

            return image, None

        path = Path(source)

        if not path.is_file():
            raise ImagePreprocessingError(
                f"Image file does not exist: {path}"
            )

        image = cv2.imread(
            str(path),
            cv2.IMREAD_UNCHANGED,
        )

        if image is None:
            raise ImagePreprocessingError(
                f"Unable to decode image file: {path}"
            )

        return image, path.suffix.lower().lstrip(".") or None

    @staticmethod
    def _to_rgb(image: np.ndarray) -> np.ndarray:
        if image.ndim == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        if image.ndim != 3:
            raise ImagePreprocessingError(
                "Unsupported image dimensions"
            )

        channels = image.shape[2]

        if channels == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if channels == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

        raise ImagePreprocessingError(
            f"Unsupported number of image channels: {channels}"
        )


__all__ = [
    "ImagePreprocessingError",
    "ImagePreprocessor",
    "PreprocessedImage",
]