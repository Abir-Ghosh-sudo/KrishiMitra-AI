from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from krishimitra_ml.common.inference import InferenceError
from .preprocessing import DiseaseImagePreprocessor


@dataclass(frozen=True, slots=True)
class DiseasePrediction:
    """Structured disease classification result."""

    disease: str
    confidence: float
    probabilities: Mapping[str, float]

    def __post_init__(self) -> None:
        if not self.disease.strip():
            raise ValueError(
                "disease cannot be empty."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1."
            )

        if not self.probabilities:
            raise ValueError(
                "probabilities cannot be empty."
            )

        for label, probability in self.probabilities.items():
            if not label.strip():
                raise ValueError(
                    "Disease labels cannot be empty."
                )

            if not 0.0 <= probability <= 1.0:
                raise ValueError(
                    f"Probability for '{label}' must be between 0 and 1."
                )


class DiseaseInferenceService:
    """
    Image-based disease inference service.

    The trained model is injected into the service. It must expose
    ``predict`` and may optionally expose ``predict_proba``.

    No treatment or pesticide recommendation is produced here.
    This layer is responsible only for disease prediction.
    """

    def __init__(
        self,
        model: object,
        *,
        labels: Sequence[str],
        preprocessor: DiseaseImagePreprocessor | None = None,
    ) -> None:
        if model is None:
            raise ValueError(
                "model cannot be None."
            )

        normalized_labels = tuple(
            label.strip()
            for label in labels
        )

        if not normalized_labels:
            raise ValueError(
                "At least one disease label is required."
            )

        if any(
            not label
            for label in normalized_labels
        ):
            raise ValueError(
                "Disease labels cannot be empty."
            )

        if len(set(normalized_labels)) != len(normalized_labels):
            raise ValueError(
                "Disease labels must be unique."
            )

        if not hasattr(model, "predict"):
            raise ValueError(
                "Disease model must expose a predict method."
            )

        self._model = model
        self._labels = normalized_labels
        self._preprocessor = (
            preprocessor
            or DiseaseImagePreprocessor()
        )

    @property
    def labels(self) -> tuple[str, ...]:
        """Return the configured disease labels."""

        return self._labels

    def predict(
        self,
        image_bytes: bytes,
    ) -> DiseasePrediction:
        """Run disease classification on an image."""

        image_tensor = self._preprocessor.process(
            image_bytes
        )

        model_input = self._prepare_model_input(
            image_tensor
        )

        try:
            raw_prediction = self._model.predict(
                model_input
            )
        except Exception as exc:
            raise InferenceError(
                "Disease model prediction failed."
            ) from exc

        disease = self._resolve_prediction(
            raw_prediction
        )

        probabilities = self._predict_probabilities(
            model_input
        )

        if probabilities:
            confidence = probabilities.get(
                disease,
                0.0,
            )
        else:
            confidence = 1.0

            probabilities = {
                disease: 1.0,
            }

        return DiseasePrediction(
            disease=disease,
            confidence=confidence,
            probabilities=probabilities,
        )

    def _prepare_model_input(
        self,
        image_tensor: object,
    ) -> list[list[float]]:
        """
        Convert the framework-independent tensor into a model input.

        The actual production adapter can replace this representation
        with a PyTorch/TensorFlow tensor without changing the service API.
        """

        data = getattr(
            image_tensor,
            "data",
            None,
        )

        if data is None:
            raise InferenceError(
                "Preprocessor returned an invalid image tensor."
            )

        return [list(data)]

    def _resolve_prediction(
        self,
        raw_prediction: object,
    ) -> str:
        """Resolve a model output to a configured disease label."""

        value = _unwrap(
            raw_prediction
        )

        if isinstance(value, str):
            if value not in self._labels:
                raise InferenceError(
                    f"Unknown disease label returned by model: {value}"
                )

            return value

        if isinstance(value, int):
            try:
                return self._labels[value]
            except IndexError as exc:
                raise InferenceError(
                    f"Invalid disease class index: {value}"
                ) from exc

        if isinstance(value, float) and value.is_integer():
            index = int(value)

            try:
                return self._labels[index]
            except IndexError as exc:
                raise InferenceError(
                    f"Invalid disease class index: {index}"
                ) from exc

        raise InferenceError(
            "Disease model returned an unsupported prediction type."
        )

    def _predict_probabilities(
        self,
        model_input: list[list[float]],
    ) -> dict[str, float]:
        """Return normalized class probabilities when available."""

        predict_proba = getattr(
            self._model,
            "predict_proba",
            None,
        )

        if predict_proba is None:
            return {}

        try:
            raw_probabilities = predict_proba(
                model_input
            )
        except Exception as exc:
            raise InferenceError(
                "Disease probability prediction failed."
            ) from exc

        values = _unwrap(
            raw_probabilities
        )

        if not isinstance(
            values,
            (list, tuple),
        ):
            raise InferenceError(
                "Disease probabilities must be a sequence."
            )

        if len(values) != len(self._labels):
            raise InferenceError(
                "Number of disease probabilities does not match "
                "the configured disease labels."
            )

        probabilities = [
            float(value)
            for value in values
        ]

        if any(
            value < 0.0 or value > 1.0
            for value in probabilities
        ):
            raise InferenceError(
                "Disease probabilities must be between 0 and 1."
            )

        total = sum(probabilities)

        if total <= 0.0:
            raise InferenceError(
                "Disease probabilities must have a positive sum."
            )

        normalized = [
            value / total
            for value in probabilities
        ]

        return dict(
            zip(
                self._labels,
                normalized,
                strict=True,
            )
        )


def _unwrap(value: object) -> object:
    """Normalize common NumPy/sklearn output containers."""

    if hasattr(value, "tolist"):
        value = value.tolist()

    if isinstance(
        value,
        (list, tuple),
    ) and len(value) == 1:
        return value[0]

    return value