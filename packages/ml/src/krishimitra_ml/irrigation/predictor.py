from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from krishimitra_ml.common.features import FeatureVector
from krishimitra_ml.common.inference import InferenceError

from .water_requirement import (
    WaterRequirementCalculator,
    WaterRequirementResult,
)


@dataclass(frozen=True, slots=True)
class IrrigationPrediction:
    """Combined irrigation prediction and water requirement result."""

    predicted_irrigation_mm: float
    water_requirement: WaterRequirementResult
    model_confidence: float | None
    requires_monitoring: bool


class IrrigationPredictor:
    """
    Application-facing irrigation prediction service.

    The injected model is responsible for learning-based prediction.
    The deterministic water requirement calculator provides a
    physically interpretable baseline.
    """

    def __init__(
        self,
        model: object | None = None,
        *,
        water_calculator: WaterRequirementCalculator | None = None,
        monitoring_threshold_mm: float = 0.0,
    ) -> None:
        if monitoring_threshold_mm < 0.0:
            raise ValueError(
                "monitoring_threshold_mm cannot be negative."
            )

        self._model = model
        self._water_calculator = (
            water_calculator
            or WaterRequirementCalculator()
        )
        self._monitoring_threshold_mm = monitoring_threshold_mm

    def predict(
        self,
        features: FeatureVector,
        *,
        reference_et_mm: float,
        crop_coefficient: float,
        rainfall_mm: float = 0.0,
        soil_water_available_mm: float = 0.0,
        previous_irrigation_mm: float = 0.0,
    ) -> IrrigationPrediction:
        """
        Generate an irrigation prediction.

        If no trained model is configured, the deterministic
        water-requirement calculation remains available as the
        baseline prediction.
        """

        if not features.values:
            raise ValueError(
                "features cannot be empty."
            )

        water_requirement = self._water_calculator.calculate(
            reference_et_mm=reference_et_mm,
            crop_coefficient=crop_coefficient,
            rainfall_mm=rainfall_mm,
            soil_water_available_mm=soil_water_available_mm,
            previous_irrigation_mm=previous_irrigation_mm,
        )

        predicted_mm = water_requirement.gross_irrigation_requirement_mm
        confidence: float | None = None

        if self._model is not None:
            predicted_mm, confidence = self._predict_with_model(
                features
            )

        predicted_mm = max(
            0.0,
            float(predicted_mm),
        )

        return IrrigationPrediction(
            predicted_irrigation_mm=round(
                predicted_mm,
                4,
            ),
            water_requirement=water_requirement,
            model_confidence=confidence,
            requires_monitoring=(
                predicted_mm > self._monitoring_threshold_mm
            ),
        )

    def predict_from_values(
        self,
        values: Sequence[float],
        *,
        feature_names: Sequence[str],
        reference_et_mm: float,
        crop_coefficient: float,
        rainfall_mm: float = 0.0,
        soil_water_available_mm: float = 0.0,
        previous_irrigation_mm: float = 0.0,
    ) -> IrrigationPrediction:
        """Generate a prediction from ordered raw feature values."""

        if len(values) != len(feature_names):
            raise ValueError(
                "values and feature_names must have the same length."
            )

        features = FeatureVector(
            names=tuple(feature_names),
            values=tuple(float(value) for value in values),
        )

        return self.predict(
            features,
            reference_et_mm=reference_et_mm,
            crop_coefficient=crop_coefficient,
            rainfall_mm=rainfall_mm,
            soil_water_available_mm=soil_water_available_mm,
            previous_irrigation_mm=previous_irrigation_mm,
        )

    def _predict_with_model(
        self,
        features: FeatureVector,
    ) -> tuple[float, float | None]:
        """Run the injected learning model safely."""

        if not hasattr(self._model, "predict"):
            raise InferenceError(
                "Configured irrigation model does not expose predict()."
            )

        try:
            raw_prediction = self._model.predict(
                [features.values]
            )
        except Exception as exc:
            raise InferenceError(
                "Irrigation model prediction failed."
            ) from exc

        try:
            predicted_value = float(raw_prediction[0])
        except (TypeError, IndexError, ValueError) as exc:
            raise InferenceError(
                "Irrigation model returned an invalid prediction."
            ) from exc

        confidence: float | None = None

        if hasattr(self._model, "predict_proba"):
            try:
                probabilities = self._model.predict_proba(
                    [features.values]
                )

                if probabilities is not None:
                    row = probabilities[0]
                    if row:
                        confidence = max(
                            float(probability)
                            for probability in row
                        )
                        confidence = min(
                            1.0,
                            max(0.0, confidence),
                        )
            except Exception:
                # Confidence is optional; prediction itself remains usable.
                confidence = None

        if predicted_value != predicted_value:
            raise InferenceError(
                "Irrigation model returned NaN."
            )

        return predicted_value, confidence


__all__ = [
    "IrrigationPrediction",
    "IrrigationPredictor",
]