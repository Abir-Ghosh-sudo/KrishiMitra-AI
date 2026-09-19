from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from krishimitra_ml.common.metrics import (
    ClassificationMetrics,
    RegressionMetrics,
    calculate_classification_metrics,
    calculate_regression_metrics,
)

from .datasets import DatasetSplit


class TrainingError(RuntimeError):
    """Raised when model training fails."""


@dataclass(frozen=True, slots=True)
class TrainingResult:
    """Result produced after training a model."""

    model: object
    task_type: str
    train_metrics: RegressionMetrics | ClassificationMetrics
    samples: int


class ModelTrainer:
    """
    Generic model trainer.

    The trainer deliberately does not instantiate a specific ML algorithm.
    A configured estimator is injected so that different models can be
    trained without coupling this package to one algorithm.
    """

    def train_regression(
        self,
        estimator: object,
        dataset: DatasetSplit,
    ) -> TrainingResult:
        """Fit a regression estimator and calculate training metrics."""

        model = self._fit(
            estimator,
            dataset.features,
            dataset.targets,
        )

        predictions = self._predict(
            model,
            dataset.features,
        )

        metrics = calculate_regression_metrics(
            dataset.targets,
            predictions,
        )

        return TrainingResult(
            model=model,
            task_type="regression",
            train_metrics=metrics,
            samples=len(dataset.targets),
        )

    def train_classification(
        self,
        estimator: object,
        dataset: DatasetSplit,
    ) -> TrainingResult:
        """Fit a classification estimator and calculate training metrics."""

        model = self._fit(
            estimator,
            dataset.features,
            dataset.targets,
        )

        predictions = self._predict(
            model,
            dataset.features,
        )

        metrics = calculate_classification_metrics(
            dataset.targets,
            predictions,
        )

        return TrainingResult(
            model=model,
            task_type="classification",
            train_metrics=metrics,
            samples=len(dataset.targets),
        )

    @staticmethod
    def _fit(
        estimator: object,
        features: Sequence[Sequence[float]],
        targets: Sequence[float],
    ) -> object:
        if not hasattr(estimator, "fit"):
            raise TrainingError(
                "Estimator must expose fit()."
            )

        try:
            fitted_model = estimator.fit(
                features,
                targets,
            )
        except Exception as exc:
            raise TrainingError(
                "Model training failed."
            ) from exc

        # Most sklearn-compatible estimators return themselves from fit().
        # Some custom estimators may return None, in which case the original
        # estimator is the trained model.
        if fitted_model is None:
            return estimator

        return fitted_model

    @staticmethod
    def _predict(
        model: object,
        features: Sequence[Sequence[float]],
    ) -> tuple[float, ...]:
        if not hasattr(model, "predict"):
            raise TrainingError(
                "Trained model must expose predict()."
            )

        try:
            raw_predictions = model.predict(
                features
            )

            if hasattr(raw_predictions, "tolist"):
                raw_predictions = raw_predictions.tolist()

            predictions = tuple(
                float(value)
                for value in raw_predictions
            )
        except (TypeError, ValueError) as exc:
            raise TrainingError(
                "Model returned invalid predictions."
            ) from exc
        except Exception as exc:
            raise TrainingError(
                "Model prediction failed."
            ) from exc

        if len(predictions) != len(features):
            raise TrainingError(
                "Prediction count does not match dataset size."
            )

        return predictions


__all__ = [
    "ModelTrainer",
    "TrainingError",
    "TrainingResult",
]