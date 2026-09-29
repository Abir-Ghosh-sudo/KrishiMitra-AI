from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


class ImageQualityError(ValueError):
    """Raised when image-quality analysis cannot be performed."""


@dataclass(frozen=True, slots=True)
class ImageQualityResult:
    """Quality assessment for a plant image."""

    score: float
    acceptable: bool
    brightness: float
    sharpness: float
    contrast: float
    reasons: tuple[str, ...] = ()


class ImageQualityAnalyzer:
    """Assess whether an image is suitable for downstream vision inference."""

    def __init__(
        self,
        *,
        minimum_score: float = 0.50,
        minimum_brightness: float = 0.10,
        maximum_brightness: float = 0.95,
        minimum_sharpness: float = 0.05,
        minimum_contrast: float = 0.08,
    ) -> None:
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError("minimum_score must be between 0 and 1")

        self._minimum_score = minimum_score
        self._minimum_brightness = minimum_brightness
        self._maximum_brightness = maximum_brightness
        self._minimum_sharpness = minimum_sharpness
        self._minimum_contrast = minimum_contrast

    def analyze(self, image: np.ndarray) -> ImageQualityResult:
        """Analyze an image represented as a NumPy array."""

        if not isinstance(image, np.ndarray):
            raise ImageQualityError("image must be a NumPy array")

        if image.size == 0:
            raise ImageQualityError("image cannot be empty")

        gray = self._to_gray(image)

        brightness = float(np.mean(gray) / 255.0)
        contrast = float(np.std(gray) / 128.0)
        contrast = min(max(contrast, 0.0), 1.0)

        laplacian_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharpness = min(laplacian_variance / 500.0, 1.0)

        reasons: list[str] = []

        if brightness < self._minimum_brightness:
            reasons.append("image_too_dark")

        if brightness > self._maximum_brightness:
            reasons.append("image_too_bright")

        if sharpness < self._minimum_sharpness:
            reasons.append("image_too_blurry")

        if contrast < self._minimum_contrast:
            reasons.append("low_contrast")

        brightness_score = self._brightness_score(brightness)
        score = (
            brightness_score * 0.30
            + sharpness * 0.40
            + contrast * 0.30
        )

        score = min(max(score, 0.0), 1.0)

        return ImageQualityResult(
            score=score,
            acceptable=score >= self._minimum_score and not reasons,
            brightness=brightness,
            sharpness=sharpness,
            contrast=contrast,
            reasons=tuple(reasons),
        )

    def _brightness_score(self, brightness: float) -> float:
        if brightness < self._minimum_brightness:
            return brightness / max(self._minimum_brightness, 1e-6)

        if brightness > self._maximum_brightness:
            excess = brightness - self._maximum_brightness
            available = 1.0 - self._maximum_brightness
            return max(0.0, 1.0 - excess / max(available, 1e-6))

        return 1.0

    @staticmethod
    def _to_gray(image: np.ndarray) -> np.ndarray:
        if image.ndim == 2:
            gray = image
        elif image.ndim == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.ndim == 3 and image.shape[2] == 4:
            gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
        else:
            raise ImageQualityError(
                "image must be grayscale, RGB, or RGBA"
            )

        if gray.dtype != np.uint8:
            gray = cv2.normalize(
                gray,
                None,
                0,
                255,
                cv2.NORM_MINMAX,
            ).astype(np.uint8)

        return gray


__all__ = [
    "ImageQualityAnalyzer",
    "ImageQualityError",
    "ImageQualityResult",
]