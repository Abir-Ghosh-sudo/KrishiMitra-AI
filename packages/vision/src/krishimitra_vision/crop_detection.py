from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class CropDetectionBackend(Protocol):
    """Protocol for a crop-identification model backend."""

    def predict(
        self,
        image: np.ndarray,
    ) -> tuple[str, float]:
        ...


class CropDetectionError(RuntimeError):
    """Raised when crop identification fails."""


@dataclass(frozen=True, slots=True)
class CropDetectionResult:
    """Crop identification result."""

    crop: str
    confidence: float
    model: str


class CropDetector:
    """Identify the crop visible in a plant image."""

    def __init__(
        self,
        backend: CropDetectionBackend,
        *,
        model_name: str = "crop-detector",
    ) -> None:
        self._backend = backend
        self._model_name = model_name

    def predict(self, image: np.ndarray) -> CropDetectionResult:
        if not isinstance(image, np.ndarray):
            raise CropDetectionError("image must be a NumPy array")

        if image.size == 0:
            raise CropDetectionError("image cannot be empty")

        try:
            crop, confidence = self._backend.predict(image)
        except Exception as exc:
            raise CropDetectionError(
                "Crop identification failed"
            ) from exc

        crop = crop.strip()

        if not crop:
            raise CropDetectionError(
                "Crop detector returned an empty crop label"
            )

        if not 0.0 <= confidence <= 1.0:
            raise CropDetectionError(
                "Crop detector returned an invalid confidence score"
            )

        return CropDetectionResult(
            crop=crop,
            confidence=float(confidence),
            model=self._model_name,
        )


__all__ = [
    "CropDetectionBackend",
    "CropDetectionError",
    "CropDetectionResult",
    "CropDetector",
]