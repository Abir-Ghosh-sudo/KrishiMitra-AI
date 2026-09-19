from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from krishimitra_ml.common.metrics import (
    ClassificationMetrics,
    RegressionMetrics,
    calculate_classification_metrics,
    calculate_regression_metrics,
)

from .datasets import DatasetSplit


class ModelValidationError(ValueError):
    """Raised when a trained model fails validation."""


@dataclass(frozen=True, slots=True)
class RegressionValidationThresholds:
    """Minimum acceptable regression-model quality thresholds."""

    max_mae: float | None = None
    max_rmse: float | None = None
    min_r2: float | None = None


@dataclass(frozen=True, slots=True)
class ClassificationValidationThresholds:
    """Minimum acceptable classification-model quality thresholds."""

    min_accuracy: float | None = None
    min_precision: float | None = None
    min_recall: float | None = None
    min_f1: float | None = None


@dataclass(frozen=True, slots=True)
class RegressionValidationResult:
    """Regression validation result."""

    metrics: RegressionMetrics
    passed: bool
    failures: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClassificationValidationResult:
    """Classification validation result."""

    metrics: ClassificationMetrics
    passed: bool
    failures: tuple[str, ...]


class ModelValidator:
    """
    Validate trained models against held-out datasets.

    Validation is intentionally separate from training. A model must
    satisfy explicit quality thresholds before it can be considered
    eligible for registration/deployment.
    """

    def validate_regression(
        self,
        model: object,
        dataset: DatasetSplit,
        *,
        thresholds: RegressionValidationThresholds | None = None,
    ) -> RegressionValidationResult:
        """Validate a regression model."""

        predictions = self._predict(
            model,
            dataset.features,
        )

        metrics = calculate_regression_metrics(
            dataset.targets,
            predictions,
        )

        failures = self._check_regression_thresholds(
            metrics,
            thresholds,
        )

        return RegressionValidationResult(
            metrics=metrics,
            passed=not failures,
            failures=tuple(failures),
        )

    def validate_classification(
        self,
        model: object,
        dataset: DatasetSplit,
        *,
        thresholds: ClassificationValidationThresholds | None = None,
    ) -> ClassificationValidationResult:
        """Validate a classification model."""

        predictions = self._predict(
            model,
            dataset.features,
        )

        metrics = calculate_classification_metrics(
            dataset.targets,
            predictions,
        )

        failures = self._check_classification_thresholds(
            metrics,
            thresholds,
        )

        return ClassificationValidationResult(
            metrics=metrics,
            passed=not failures,
            failures=tuple(failures),
        )

    @staticmethod
    def _predict(
        model: object,
        features: Sequence[Sequence[float]],
    ) -> tuple[float, ...]:
        if not hasattr(model, "predict"):
            raise ModelValidationError(
                "Model must expose predict()."
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
            raise ModelValidationError(
                "Model returned invalid predictions."
            ) from exc
        except Exception as exc:
            raise ModelValidationError(
                "Model prediction failed during validation."
            ) from exc

        if not predictions:
            raise ModelValidationError(
                "Model returned no predictions."
            )

        if not all(
            isfinite(value)
            for value in predictions
        ):
            raise ModelValidationError(
                "Model returned non-finite predictions."
            )

        if len(predictions) != len(features):
            raise ModelValidationError(
                "Prediction count does not match dataset size."
            )

        return predictions

    @staticmethod
    def _check_regression_thresholds(
        metrics: RegressionMetrics,
        thresholds: RegressionValidationThresholds | None,
    ) -> list[str]:
        if thresholds is None:
            return []

        failures: list[str] = []

        if (
            thresholds.max_mae is not None
            and metrics.mae > thresholds.max_mae
        ):
            failures.append(
                f"MAE {metrics.mae:.6f} exceeds "
                f"maximum {thresholds.max_mae:.6f}."
            )

        if (
            thresholds.max_rmse is not None
            and metrics.rmse > thresholds.max_rmse
        ):
            failures.append(
                f"RMSE {metrics.rmse:.6f} exceeds "
                f"maximum {thresholds.max_rmse:.6f}."
            )

        if (
            thresholds.min_r2 is not None
            and metrics.r2 < thresholds.min_r2
        ):
            failures.append(
                f"R² {metrics.r2:.6f} is below "
                f"minimum {thresholds.min_r2:.6f}."
            )

        return failures

    @staticmethod
    def _check_classification_thresholds(
        metrics: ClassificationMetrics,
        thresholds: ClassificationValidationThresholds | None,
    ) -> list[str]:
        if thresholds is None:
            return []

        failures: list[str] = []

        if (
            thresholds.min_accuracy is not None
            and metrics.accuracy < thresholds.min_accuracy
        ):
            failures.append(
                f"Accuracy {metrics.accuracy:.6f} is below "
                f"minimum {thresholds.min_accuracy:.6f}."
            )

        if (
            thresholds.min_precision is not None
            and metrics.precision < thresholds.min_precision
        ):
            failures.append(
                f"Precision {metrics.precision:.6f} is below "
                f"minimum {thresholds.min_precision:.6f}."
            )

        if (
            thresholds.min_recall is not None
            and metrics.recall < thresholds.min_recall
        ):
            failures.append(
                f"Recall {metrics.recall:.6f} is below "
                f"minimum {thresholds.min_recall:.6f}."
            )

        if (
            thresholds.min_f1 is not None
            and metrics.f1 < thresholds.min_f1
        ):
            failures.append(
                f"F1 {metrics.f1:.6f} is below "
                f"minimum {thresholds.min_f1:.6f}."
            )

        return failures


__all__ = [
    "ClassificationValidationResult",
    "ClassificationValidationThresholds",
    "ModelValidationError",
    "ModelValidator",
    "RegressionValidationResult",
    "RegressionValidationThresholds",
]