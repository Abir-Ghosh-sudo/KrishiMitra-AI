from __future__ import annotations

from dataclasses import dataclass

from krishimitra_ml.common.features import FeatureVector
from krishimitra_ml.common.inference import InferenceError

from .consumption import (
    EnergyConsumptionCalculator,
    EnergyConsumptionInput,
    EnergyConsumptionResult,
)


@dataclass(frozen=True, slots=True)
class EnergyPrediction:
    """Combined energy prediction and deterministic baseline."""

    predicted_energy_kwh: float
    baseline: EnergyConsumptionResult
    model_confidence: float | None
    model_used: bool


class EnergyPredictor:
    """
    Application-facing energy prediction service.

    A trained model may be injected for learned predictions.
    The deterministic hydraulic-energy calculation remains available
    as a transparent baseline.
    """

    def __init__(
        self,
        model: object | None = None,
        *,
        consumption_calculator: EnergyConsumptionCalculator | None = None,
    ) -> None:
        self._model = model
        self._calculator = (
            consumption_calculator
            or EnergyConsumptionCalculator()
        )

    def predict(
        self,
        features: FeatureVector,
        *,
        consumption_input: EnergyConsumptionInput,
    ) -> EnergyPrediction:
        """Predict irrigation energy consumption."""

        if not features.values:
            raise ValueError(
                "features cannot be empty."
            )

        baseline = self._calculator.calculate(
            consumption_input
        )

        if self._model is None:
            return EnergyPrediction(
                predicted_energy_kwh=baseline.electrical_energy_kwh,
                baseline=baseline,
                model_confidence=None,
                model_used=False,
            )

        predicted_energy, confidence = (
            self._predict_with_model(features)
        )

        if predicted_energy < 0.0:
            raise InferenceError(
                "Energy model returned a negative prediction."
            )

        return EnergyPrediction(
            predicted_energy_kwh=round(
                predicted_energy,
                6,
            ),
            baseline=baseline,
            model_confidence=confidence,
            model_used=True,
        )

    def _predict_with_model(
        self,
        features: FeatureVector,
    ) -> tuple[float, float | None]:
        """Run the injected energy model."""

        if not hasattr(self._model, "predict"):
            raise InferenceError(
                "Configured energy model does not expose predict()."
            )

        try:
            raw_prediction = self._model.predict(
                [features.values]
            )
        except Exception as exc:
            raise InferenceError(
                "Energy model prediction failed."
            ) from exc

        try:
            predicted_energy = float(
                raw_prediction[0]
            )
        except (TypeError, IndexError, ValueError) as exc:
            raise InferenceError(
                "Energy model returned an invalid prediction."
            ) from exc

        if not predicted_energy == predicted_energy:
            raise InferenceError(
                "Energy model returned NaN."
            )

        confidence = self._extract_confidence(
            features
        )

        return predicted_energy, confidence

    def _extract_confidence(
        self,
        features: FeatureVector,
    ) -> float | None:
        """Extract optional confidence from classification-style models."""

        if not hasattr(self._model, "predict_proba"):
            return None

        try:
            probabilities = self._model.predict_proba(
                [features.values]
            )

            if probabilities is None:
                return None

            row = probabilities[0]

            if len(row) == 0:
                return None

            confidence = max(
                float(probability)
                for probability in row
            )

            return min(
                1.0,
                max(0.0, confidence),
            )
        except Exception:
            return None


__all__ = [
    "EnergyPrediction",
    "EnergyPredictor",
]