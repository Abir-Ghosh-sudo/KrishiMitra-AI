from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class DiseaseDetectionBackend(Protocol):
    """Protocol for a plant-disease model backend."""

    def predict(
        self,
        image: np.ndarray,
    ) -> tuple[str, float]:
        ...


class DiseaseDetectionError(RuntimeError):
    """Raised when disease detection fails."""


@dataclass(frozen=True, slots=True)
class DiseaseDetectionResult:
    """Disease classification result."""

    disease: str
    confidence: float
    model: str


class DiseaseDetector:
    """Detect a plant disease from a processed image."""

    def __init__(
        self,
        backend: DiseaseDetectionBackend,
        *,
        model_name: str = "disease-detector",
        minimum_confidence: float = 0.60,
    ) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError(
                "minimum_confidence must be between 0 and 1"
            )

        self._backend = backend
        self._model_name = model_name
        self._minimum_confidence = minimum_confidence

    def predict(self, image: np.ndarray) -> DiseaseDetectionResult:
        if not isinstance(image, np.ndarray):
            raise DiseaseDetectionError("image must be a NumPy array")

        if image.size == 0:
            raise DiseaseDetectionError("image cannot be empty")

        try:
            disease, confidence = self._backend.predict(image)
        except Exception as exc:
            raise DiseaseDetectionError(
                "Disease detection failed"
            ) from exc

        disease = disease.strip()

        if not disease:
            raise DiseaseDetectionError(
                "Disease detector returned an empty label"
            )

        if not 0.0 <= confidence <= 1.0:
            raise DiseaseDetectionError(
                "Disease detector returned an invalid confidence score"
            )

        return DiseaseDetectionResult(
            disease=disease,
            confidence=float(confidence),
            model=self._model_name,
        )

    def is_reliable(self, result: DiseaseDetectionResult) -> bool:
        """Return whether the disease prediction meets the confidence threshold."""

        return result.confidence >= self._minimum_confidence


__all__ = [
    "DiseaseDetectionBackend",
    "DiseaseDetectionError",
    "DiseaseDetectionResult",
    "DiseaseDetector",
]