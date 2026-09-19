from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from krishimitra_ml.common.inference import InferenceError
from krishimitra_ml.common.metrics import ClassificationMetrics


@dataclass(frozen=True, slots=True)
class CropStagePrediction:
    """Prediction result for a crop growth stage."""

    stage: str
    confidence: float
    probabilities: Mapping[str, float]

    def __post_init__(self) -> None:
        if not self.stage.strip():
            raise ValueError("stage cannot be empty.")

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
                    "Probability labels cannot be empty."
                )

            if not 0.0 <= probability <= 1.0:
                raise ValueError(
                    f"Probability for '{label}' must be between 0 and 1."
                )


class CropStageClassifier:
    """
    Crop-stage classification service.

    The classifier accepts a model artifact exposing ``predict`` and,
    optionally, ``predict_proba``. The actual trained model is injected
    at runtime so this package remains independent of a particular
    training framework.
    """

    def __init__(
        self,
        model: object,
        *,
        stage_labels: Sequence[str],
    ) -> None:
        if model is None:
            raise ValueError("model cannot be None.")

        labels = tuple(
            label.strip()
            for label in stage_labels
        )

        if not labels:
            raise ValueError(
                "At least one crop stage label is required."
            )

        if any(not label for label in labels):
            raise ValueError(
                "Crop stage labels cannot be empty."
            )

        if len(set(labels)) != len(labels):
            raise ValueError(
                "Crop stage labels must be unique."
            )

        self._model = model
        self._stage_labels = labels

    @property
    def stage_labels(self) -> tuple[str, ...]:
        """Return supported crop-stage labels."""

        return self._stage_labels

    def predict(
        self,
        features: Sequence[float],
    ) -> CropStagePrediction:
        """Predict the crop growth stage."""

        if not features:
            raise ValueError(
                "features cannot be empty."
            )

        values = tuple(
            float(value)
            for value in features
        )

        if any(
            not _is_finite(value)
            for value in values
        ):
            raise ValueError(
                "features must contain only finite numeric values."
            )

        try:
            raw_prediction = self._model.predict(
                [list(values)]
            )
        except Exception as exc:
            raise InferenceError(
                "Crop-stage model prediction failed."
            ) from exc

        stage = self._resolve_stage(
            raw_prediction
        )

        probabilities = self._predict_probabilities(
            values
        )

        confidence = probabilities.get(
            stage,
            1.0 if len(probabilities) == 1 else 0.0,
        )

        return CropStagePrediction(
            stage=stage,
            confidence=confidence,
            probabilities=probabilities,
        )

    def evaluate(
        self,
        features: Sequence[Sequence[float]],
        labels: Sequence[str],
    ) -> ClassificationMetrics:
        """Evaluate the classifier on labelled samples."""

        if not features:
            raise ValueError(
                "features cannot be empty."
            )

        if len(features) != len(labels):
            raise ValueError(
                "features and labels must have the same length."
            )

        predictions = [
            self.predict(sample).stage
            for sample in features
        ]

        return _classification_metrics(
            labels,
            predictions,
        )

    def _resolve_stage(
        self,
        raw_prediction: object,
    ) -> str:
        """Convert a model prediction into a known crop-stage label."""

        value = _unwrap_prediction(raw_prediction)

        if isinstance(value, str):
            if value not in self._stage_labels:
                raise InferenceError(
                    f"Unknown crop stage returned by model: {value}"
                )

            return value

        if isinstance(value, int):
            try:
                return self._stage_labels[value]
            except IndexError as exc:
                raise InferenceError(
                    f"Model returned invalid crop-stage index: {value}"
                ) from exc

        if isinstance(value, float) and value.is_integer():
            index = int(value)

            try:
                return self._stage_labels[index]
            except IndexError as exc:
                raise InferenceError(
                    f"Model returned invalid crop-stage index: {index}"
                ) from exc

        raise InferenceError(
            "Crop-stage model returned an unsupported prediction type."
        )

    def _predict_probabilities(
        self,
        features: Sequence[float],
    ) -> dict[str, float]:
        """Return class probabilities when the model supports them."""

        predict_proba = getattr(
            self._model,
            "predict_proba",
            None,
        )

        if predict_proba is None:
            return {}

        try:
            raw_probabilities = predict_proba(
                [list(features)]
            )
        except Exception as exc:
            raise InferenceError(
                "Crop-stage probability prediction failed."
            ) from exc

        probabilities = _unwrap_prediction(
            raw_probabilities
        )

        if not isinstance(probabilities, (list, tuple)):
            raise InferenceError(
                "Model probabilities must be a sequence."
            )

        if len(probabilities) != len(self._stage_labels):
            raise InferenceError(
                "Number of model probabilities does not match "
                "the configured crop-stage labels."
            )

        values = [
            float(probability)
            for probability in probabilities
        ]

        if any(
            not _is_finite(value) or not 0.0 <= value <= 1.0
            for value in values
        ):
            raise InferenceError(
                "Model returned invalid crop-stage probabilities."
            )

        total = sum(values)

        if total <= 0:
            raise InferenceError(
                "Crop-stage probabilities must have a positive sum."
            )

        normalized = [
            value / total
            for value in values
        ]

        return dict(
            zip(
                self._stage_labels,
                normalized,
                strict=True,
            )
        )


def _unwrap_prediction(
    value: object,
) -> object:
    """Normalize common NumPy/sklearn prediction containers."""

    if hasattr(value, "tolist"):
        value = value.tolist()

    if isinstance(value, (list, tuple)) and len(value) == 1:
        return value[0]

    return value


def _classification_metrics(
    y_true: Sequence[str],
    y_pred: Sequence[str],
) -> ClassificationMetrics:
    """Calculate macro-style metrics across configured labels."""

    if not y_true:
        raise ValueError(
            "y_true cannot be empty."
        )

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must have the same length."
        )

    labels = tuple(
        sorted(
            set(y_true) | set(y_pred)
        )
    )

    accuracy = sum(
        actual == predicted
        for actual, predicted in zip(
            y_true,
            y_pred,
            strict=True,
        )
    ) / len(y_true)

    precision_values: list[float] = []
    recall_values: list[float] = []
    f1_values: list[float] = []

    for label in labels:
        true_positive = sum(
            actual == label and predicted == label
            for actual, predicted in zip(
                y_true,
                y_pred,
                strict=True,
            )
        )

        false_positive = sum(
            actual != label and predicted == label
            for actual, predicted in zip(
                y_true,
                y_pred,
                strict=True,
            )
        )

        false_negative = sum(
            actual == label and predicted != label
            for actual, predicted in zip(
                y_true,
                y_pred,
                strict=True,
            )
        )

        precision_denominator = (
            true_positive + false_positive
        )
        recall_denominator = (
            true_positive + false_negative
        )

        precision = (
            true_positive / precision_denominator
            if precision_denominator
            else 0.0
        )

        recall = (
            true_positive / recall_denominator
            if recall_denominator
            else 0.0
        )

        f1_denominator = precision + recall

        f1 = (
            2.0 * precision * recall / f1_denominator
            if f1_denominator
            else 0.0
        )

        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)

    return ClassificationMetrics(
        accuracy=accuracy,
        precision=sum(precision_values) / len(precision_values),
        recall=sum(recall_values) / len(recall_values),
        f1=sum(f1_values) / len(f1_values),
    )


def _is_finite(value: float) -> bool:
    """Check whether a numeric value is finite."""

    return value == value and abs(value) != float("inf")