from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from krishimitra_ml.common.metrics import (
    ClassificationMetrics,
    calculate_classification_metrics,
)
from .inference import DiseaseInferenceService, DiseasePrediction


@dataclass(frozen=True, slots=True)
class DiseaseClassifierConfig:
    """Configuration for production disease classification."""

    confidence_threshold: float = 0.70
    expert_escalation_threshold: float = 0.50

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                "confidence_threshold must be between 0 and 1."
            )

        if not 0.0 <= self.expert_escalation_threshold <= 1.0:
            raise ValueError(
                "expert_escalation_threshold must be between 0 and 1."
            )

        if (
            self.expert_escalation_threshold
            > self.confidence_threshold
        ):
            raise ValueError(
                "expert_escalation_threshold cannot exceed "
                "confidence_threshold."
            )


@dataclass(frozen=True, slots=True)
class DiseaseClassificationResult:
    """Safe classification result with escalation information."""

    prediction: DiseasePrediction
    accepted: bool
    requires_expert_review: bool
    confidence_threshold: float


class DiseaseClassifier:
    """
    Production-facing disease classification abstraction.

    This class deliberately does not recommend treatments. It only
    determines whether the visual model prediction is sufficiently
    confident to be accepted or escalated for further review.
    """

    def __init__(
        self,
        inference_service: DiseaseInferenceService,
        *,
        config: DiseaseClassifierConfig | None = None,
    ) -> None:
        self._inference_service = inference_service
        self._config = (
            config
            or DiseaseClassifierConfig()
        )

    @property
    def config(self) -> DiseaseClassifierConfig:
        """Return classifier configuration."""

        return self._config

    @property
    def labels(self) -> tuple[str, ...]:
        """Return supported disease labels."""

        return self._inference_service.labels

    def classify(
        self,
        image_bytes: bytes,
    ) -> DiseaseClassificationResult:
        """Classify a plant image and determine confidence handling."""

        prediction = self._inference_service.predict(
            image_bytes
        )

        confidence = prediction.confidence

        accepted = (
            confidence >= self._config.confidence_threshold
        )

        requires_expert_review = (
            confidence < self._config.expert_escalation_threshold
        )

        return DiseaseClassificationResult(
            prediction=prediction,
            accepted=accepted,
            requires_expert_review=requires_expert_review,
            confidence_threshold=(
                self._config.confidence_threshold
            ),
        )

    def evaluate(
        self,
        images: Sequence[bytes],
        true_labels: Sequence[str],
    ) -> ClassificationMetrics:
        """Evaluate the disease classifier on labelled images."""

        if not images:
            raise ValueError(
                "images cannot be empty."
            )

        if len(images) != len(true_labels):
            raise ValueError(
                "images and true_labels must have the same length."
            )

        predictions = [
            self._inference_service.predict(
                image
            ).disease
            for image in images
        ]

        return calculate_classification_metrics(
            true_labels,
            predictions,
        )

    def confidence_summary(
        self,
        image_bytes: bytes,
    ) -> Mapping[str, float]:
        """Return the model probability distribution for an image."""

        prediction = self._inference_service.predict(
            image_bytes
        )

        return dict(
            prediction.probabilities
        )