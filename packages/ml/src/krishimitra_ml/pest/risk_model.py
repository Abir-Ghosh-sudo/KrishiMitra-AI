from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Sequence


class PestRiskLevel(StrEnum):
    """Qualitative pest-risk levels."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class InferenceError(RuntimeError):
    """Raised when pest-risk inference fails."""


@dataclass(frozen=True, slots=True)
class PestRiskPrediction:
    """Prediction produced by the pest-risk model."""

    risk_score: float
    risk_level: PestRiskLevel
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not isfinite(self.risk_score):
            raise ValueError(
                "risk_score must be finite."
            )

        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError(
                "risk_score must be between 0 and 1."
            )

        if self.confidence is not None:
            if not isfinite(self.confidence):
                raise ValueError(
                    "confidence must be finite."
                )

            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "confidence must be between 0 and 1."
                )


class PestRiskModel:
    """
    Adapter around an injected pest-risk estimator.

    The estimator is expected to expose predict(). If predict_proba()
    exists, its probability information is used as confidence when
    available.
    """

    def __init__(
        self,
        model: object,
        *,
        confidence_threshold: float = 0.60,
    ) -> None:
        if not hasattr(model, "predict"):
            raise ValueError(
                "Pest risk model must expose predict()."
            )

        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(
                "confidence_threshold must be between 0 and 1."
            )

        self._model = model
        self.confidence_threshold = confidence_threshold

    def predict(
        self,
        features: Sequence[Sequence[float]],
    ) -> PestRiskPrediction:
        """Generate a pest-risk prediction."""

        if not features:
            raise ValueError(
                "features cannot be empty."
            )

        try:
            raw_prediction = self._model.predict(
                features
            )
        except Exception as exc:
            raise InferenceError(
                "Pest risk model prediction failed."
            ) from exc

        values = self._to_values(
            raw_prediction
        )

        if not values:
            raise InferenceError(
                "Pest risk model returned no prediction."
            )

        risk_score = self._normalize_prediction(
            values[0]
        )

        confidence = self._extract_confidence(
            features
        )

        return PestRiskPrediction(
            risk_score=risk_score,
            risk_level=self._risk_level(
                risk_score
            ),
            confidence=confidence,
        )

    @staticmethod
    def _to_values(
        prediction: object,
    ) -> tuple[object, ...]:
        if hasattr(prediction, "tolist"):
            prediction = prediction.tolist()

        if isinstance(prediction, (list, tuple)):
            if (
                prediction
                and isinstance(
                    prediction[0],
                    (list, tuple),
                )
            ):
                return tuple(prediction[0])

            return tuple(prediction)

        return (prediction,)

    @staticmethod
    def _normalize_prediction(
        value: object,
    ) -> float:
        if isinstance(value, str):
            label = value.strip().lower()

            mapping = {
                "low": 0.125,
                "moderate": 0.375,
                "medium": 0.375,
                "high": 0.625,
                "critical": 0.875,
            }

            if label in mapping:
                return mapping[label]

            try:
                value = float(value)
            except ValueError as exc:
                raise InferenceError(
                    f"Unsupported pest-risk label: {value}"
                ) from exc

        try:
            score = float(value)
        except (TypeError, ValueError) as exc:
            raise InferenceError(
                "Pest-risk prediction is not numeric."
            ) from exc

        if not isfinite(score):
            raise InferenceError(
                "Pest-risk prediction must be finite."
            )

        # Some classifiers return class indexes.
        if score.is_integer() and score in {0.0, 1.0, 2.0, 3.0}:
            return {
                0.0: 0.125,
                1.0: 0.375,
                2.0: 0.625,
                3.0: 0.875,
            }[score]

        return max(
            0.0,
            min(1.0, score),
        )

    def _extract_confidence(
        self,
        features: Sequence[Sequence[float]],
    ) -> float | None:
        if not hasattr(
            self._model,
            "predict_proba",
        ):
            return None

        try:
            probabilities = self._model.predict_proba(
                features
            )

            if hasattr(probabilities, "tolist"):
                probabilities = probabilities.tolist()

            if not probabilities:
                return None

            first = probabilities[0]

            if not isinstance(
                first,
                (list, tuple),
            ):
                return None

            confidence = max(
                float(value)
                for value in first
            )

            if not isfinite(confidence):
                return None

            return max(
                0.0,
                min(1.0, confidence),
            )
        except Exception:
            return None

    @staticmethod
    def _risk_level(
        score: float,
    ) -> PestRiskLevel:
        if score < 0.25:
            return PestRiskLevel.LOW

        if score < 0.50:
            return PestRiskLevel.MODERATE

        if score < 0.75:
            return PestRiskLevel.HIGH

        return PestRiskLevel.CRITICAL


__all__ = [
    "InferenceError",
    "PestRiskLevel",
    "PestRiskModel",
    "PestRiskPrediction",
]