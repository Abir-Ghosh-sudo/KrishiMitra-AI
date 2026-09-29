from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


class MultiImageError(ValueError):
    """Raised when multi-image analysis input is invalid."""


@dataclass(frozen=True, slots=True)
class MultiImageResult:
    """Aggregated representation of multiple plant images."""

    image_count: int
    images: tuple[np.ndarray, ...]


class MultiImageAnalyzer:
    """
    Validate and prepare multiple images for joint visual analysis.

    Actual cross-image model inference belongs to the downstream
    disease/pest/vision orchestration layer.
    """

    def __init__(
        self,
        *,
        minimum_images: int = 1,
        maximum_images: int = 8,
    ) -> None:
        if minimum_images < 1:
            raise ValueError("minimum_images must be at least 1")

        if maximum_images < minimum_images:
            raise ValueError(
                "maximum_images must be >= minimum_images"
            )

        self._minimum_images = minimum_images
        self._maximum_images = maximum_images

    def prepare(
        self,
        images: Sequence[np.ndarray],
    ) -> MultiImageResult:
        if not images:
            raise MultiImageError("At least one image is required")

        if len(images) < self._minimum_images:
            raise MultiImageError(
                f"At least {self._minimum_images} image(s) are required"
            )

        if len(images) > self._maximum_images:
            raise MultiImageError(
                f"At most {self._maximum_images} images are supported"
            )

        validated: list[np.ndarray] = []

        for index, image in enumerate(images):
            if not isinstance(image, np.ndarray):
                raise MultiImageError(
                    f"Image at index {index} must be a NumPy array"
                )

            if image.size == 0:
                raise MultiImageError(
                    f"Image at index {index} cannot be empty"
                )

            validated.append(image)

        return MultiImageResult(
            image_count=len(validated),
            images=tuple(validated),
        )


__all__ = [
    "MultiImageAnalyzer",
    "MultiImageError",
    "MultiImageResult",
]