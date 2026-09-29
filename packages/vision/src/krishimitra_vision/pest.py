from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class PestDetectionBackend(Protocol):
    """Protocol for a plant-pest detection model backend."""

    def predict(
        self,
        image: np.ndarray,
    ) -> tuple[str, float]:
        ...


class PestDetectionError(RuntimeError):
    """Raised when pest detection fails."""


@dataclass(frozen=True, slots=True)
class PestDetectionResult:
    """Pest identification result."""

    pest: str
    confidence: float
    model: str


class PestDetector:
    """Detect a pest from a processed agricultural image."""

    def __init__(
        self,
        backend: PestDetectionBackend,
        *,
        model_name: str = "pest-detector",
        minimum_confidence: float = 0.60,
    ) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError(
                "minimum_confidence must be between 0 and 1"
            )

        self._backend = backend
        self._model_name = model_name
        self._minimum_confidence = minimum_confidence

    def predict(self, image: np.ndarray) -> PestDetectionResult:
        if not isinstance(image, np.ndarray):
            raise PestDetectionError("image must be a NumPy array")

        if image.size == 0:
            raise PestDetectionError("image cannot be empty")

        try:
            pest, confidence = self._backend.predict(image)
        except Exception as exc:
            raise PestDetectionError(
                "Pest detection failed"
            ) from exc

        pest = pest.strip()

        if not pest:
            raise PestDetectionError(
                "Pest detector returned an empty label"
            )

        if not 0.0 <= confidence <= 1.0:
            raise PestDetectionError(
                "Pest detector returned an invalid confidence score"
            )

        return PestDetectionResult(
            pest=pest,
            confidence=float(confidence),
            model=self._model_name,
        )

    def is_reliable(self, result: PestDetectionResult) -> bool:
        """Return whether the pest prediction meets the confidence threshold."""

        return result.confidence >= self._minimum_confidence


__all__ = [
    "PestDetectionBackend",
    "PestDetectionError",
    "PestDetectionResult",
    "PestDetector",
]