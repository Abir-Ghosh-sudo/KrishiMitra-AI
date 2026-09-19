from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from krishimitra_ml.common.features import FeatureVector
from krishimitra_ml.common.inference import InferenceError

from .risk_model import PestRiskLevel, PestRiskModel, PestRiskPrediction


@dataclass(frozen=True, slots=True)
class PestPrediction:
    """Complete pest prediction result."""

    risk: PestRiskPrediction
    actionable: bool
    requires_monitoring: bool
    requires_expert_review: bool


class PestPredictor:
    """
    Application-facing pest prediction service.

    This service combines the deterministic feature pipeline with the
    pest-risk model and applies confidence/monitoring thresholds.

    Pest identification from images is intentionally separate from
    environmental pest-risk prediction.
    """

    def __init__(
        self,
        risk_model: PestRiskModel,
        *,
        actionable_threshold: float = 0.50,
        expert_review_threshold: float = 0.40,
    ) -> None:
        if not 0.0 <= actionable_threshold <= 1.0:
            raise ValueError(
                "actionable_threshold must be between 0 and 1."
            )

        if not 0.0 <= expert_review_threshold <= 1.0:
            raise ValueError(
                "expert_review_threshold must be between 0 and 1."
            )

        if expert_review_threshold > actionable_threshold:
            raise ValueError(
                "expert_review_threshold cannot exceed "
                "actionable_threshold."
            )

        self._risk_model = risk_model
        self._actionable_threshold = actionable_threshold
        self._expert_review_threshold = expert_review_threshold

    def predict(
        self,
        features: FeatureVector,
    ) -> PestPrediction:
        """Generate a pest-risk prediction from prepared features."""

        if not features.values:
            raise ValueError(
                "features cannot be empty."
            )

        try:
            risk = self._risk_model.predict(
                features
            )
        except InferenceError:
            raise
        except Exception as exc:
            raise InferenceError(
                "Pest prediction failed."
            ) from exc

        return self._build_result(
            risk
        )

    def predict_from_values(
        self,
        values: Sequence[float],
        *,
        feature_names: Sequence[str],
    ) -> PestPrediction:
        """
        Generate a prediction from raw feature values.

        FeatureVector remains the canonical internal representation.
        """

        if len(values) != len(feature_names):
            raise ValueError(
                "values and feature_names must have the same length."
            )

        from krishimitra_ml.common.features import FeatureVector

        features = FeatureVector(
            names=tuple(feature_names),
            values=tuple(float(value) for value in values),
        )

        return self.predict(
            features
        )

    def _build_result(
        self,
        risk: PestRiskPrediction,
    ) -> PestPrediction:
        """Convert model output into operational handling flags."""

        actionable = (
            risk.risk_score
            >= self._actionable_threshold
        )

        requires_expert_review = (
            risk.risk_score
            < self._expert_review_threshold
            and risk.confidence < self._actionable_threshold
        )

        requires_monitoring = (
            risk.risk_level
            in {
                PestRiskLevel.MODERATE,
                PestRiskLevel.HIGH,
                PestRiskLevel.CRITICAL,
            }
        )

        return PestPrediction(
            risk=risk,
            actionable=actionable,
            requires_monitoring=requires_monitoring,
            requires_expert_review=requires_expert_review,
        )