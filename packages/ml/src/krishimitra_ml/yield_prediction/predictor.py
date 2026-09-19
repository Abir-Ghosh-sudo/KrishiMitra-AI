from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from krishimitra_ml.common.features import FeatureVector
from krishimitra_ml.common.inference import InferenceError

from .uncertainty import (
    YieldUncertainty,
    YieldUncertaintyEstimator,
)


@dataclass(frozen=True, slots=True)
class YieldPrediction:
    """Complete yield prediction with uncertainty information."""

    predicted_yield: float
    uncertainty: YieldUncertainty
    model_used: bool


class YieldPredictor:
    """
    Application-facing yield prediction service.

    A trained model is injected at runtime. If the model supports
    ensemble-style predictions, those predictions are used to estimate
    uncertainty. A single model prediction remains valid, but its
    empirical model uncertainty is zero and should not be interpreted
    as proof of certainty.
    """

    def __init__(
        self,
        model: object | None = None,
        *,
        uncertainty_estimator: YieldUncertaintyEstimator | None = None,
        confidence_level: float = 0.95,
    ) -> None:
        if not 0.0 < confidence_level < 1.0:
            raise ValueError(
                "confidence_level must be between 0 and 1."
            )

        self._model = model
        self._uncertainty_estimator = (
            uncertainty_estimator
            or YieldUncertaintyEstimator()
        )
        self._confidence_level = confidence_level

    def predict(
        self,
        features: FeatureVector,
    ) -> YieldPrediction:
        """Generate a yield prediction from prepared features."""

        if not features.values:
            raise ValueError(
                "features cannot be empty."
            )

        if self._model is None:
            raise InferenceError(
                "A trained yield model is required for prediction."
            )

        predictions = self._predict_model(
            features
        )

        uncertainty = self._uncertainty_estimator.estimate(
            predictions,
            confidence_level=self._confidence_level,
        )

        return YieldPrediction(
            predicted_yield=uncertainty.point_estimate,
            uncertainty=uncertainty,
            model_used=True,
        )

    def predict_from_values(
        self,
        values: Sequence[float],
        *,
        feature_names: Sequence[str],
    ) -> YieldPrediction:
        """Generate a yield prediction from ordered feature values."""

        if len(values) != len(feature_names):
            raise ValueError(
                "values and feature_names must have the same length."
            )

        features = FeatureVector(
            names=tuple(feature_names),
            values=tuple(float(value) for value in values),
        )

        return self.predict(
            features
        )

    def _predict_model(
        self,
        features: FeatureVector,
    ) -> tuple[float, ...]:
        """Extract one or more predictions from the configured model."""

        if not hasattr(self._model, "predict"):
            raise InferenceError(
                "Configured yield model does not expose predict()."
            )

        # Ensemble-capable models may expose predict_ensemble().
        if hasattr(self._model, "predict_ensemble"):
            try:
                raw_predictions = self._model.predict_ensemble(
                    [features.values]
                )
            except Exception as exc:
                raise InferenceError(
                    "Yield ensemble prediction failed."
                ) from exc

            predictions = self._normalize_predictions(
                raw_predictions
            )
        else:
            try:
                raw_prediction = self._model.predict(
                    [features.values]
                )
            except Exception as exc:
                raise InferenceError(
                    "Yield model prediction failed."
                ) from exc

            predictions = self._normalize_predictions(
                raw_prediction
            )

        if not predictions:
            raise InferenceError(
                "Yield model returned no predictions."
            )

        return predictions

    @staticmethod
    def _normalize_predictions(
        raw_predictions: object,
    ) -> tuple[float, ...]:
        """Normalize model output into finite non-negative predictions."""

        try:
            if hasattr(raw_predictions, "tolist"):
                raw_predictions = raw_predictions.tolist()

            if isinstance(raw_predictions, (int, float)):
                values = (float(raw_predictions),)
            else:
                values = tuple(
                    float(value)
                    for value in raw_predictions  # type: ignore[union-attr]
                )
        except (TypeError, ValueError) as exc:
            raise InferenceError(
                "Yield model returned an invalid prediction."
            ) from exc

        for value in values:
            if value != value:
                raise InferenceError(
                    "Yield model returned NaN."
                )

            if value < 0.0:
                raise InferenceError(
                    "Yield model returned a negative prediction."
                )

        return values


__all__ = [
    "YieldPrediction",
    "YieldPredictor",
]