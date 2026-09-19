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

from .datasets import DatasetSplit, DatasetValidationError


class CrossValidationError(ValueError):
    """Raised when cross-validation cannot be performed safely."""


@dataclass(frozen=True, slots=True)
class RegressionFoldResult:
    """Evaluation result for one regression fold."""

    fold: int
    metrics: RegressionMetrics
    sample_count: int


@dataclass(frozen=True, slots=True)
class ClassificationFoldResult:
    """Evaluation result for one classification fold."""

    fold: int
    metrics: ClassificationMetrics
    sample_count: int


@dataclass(frozen=True, slots=True)
class RegressionCrossValidationResult:
    """Aggregated regression cross-validation result."""

    folds: tuple[RegressionFoldResult, ...]
    mean_mae: float
    mean_rmse: float
    mean_r2: float


@dataclass(frozen=True, slots=True)
class ClassificationCrossValidationResult:
    """Aggregated classification cross-validation result."""

    folds: tuple[ClassificationFoldResult, ...]
    mean_accuracy: float
    mean_precision: float
    mean_recall: float
    mean_f1: float


class CrossValidator:
    """
    Lightweight deterministic cross-validation utility.

    The estimator is injected and must expose:
        fit(features, targets)
        predict(features)

    The class intentionally avoids hidden random state so experiments
    remain reproducible when deterministic folds are supplied.
    """

    def __init__(
        self,
        *,
        folds: int = 5,
    ) -> None:
        if folds < 2:
            raise ValueError(
                "folds must be at least 2."
            )

        self._folds = folds

    def regression(
        self,
        dataset: DatasetSplit,
        estimator: object,
    ) -> RegressionCrossValidationResult:
        """Run deterministic k-fold regression validation."""

        self._validate_dataset(dataset)

        fold_indices = self._build_folds(
            dataset.sample_count
        )

        results: list[RegressionFoldResult] = []

        for fold_number, validation_indices in enumerate(
            fold_indices,
            start=1,
        ):
            training_indices = tuple(
                index
                for index in range(dataset.sample_count)
                if index not in validation_indices
            )

            if not training_indices:
                raise CrossValidationError(
                    "A training fold cannot be empty."
                )

            model = self._clone_estimator(
                estimator
            )

            train_features = tuple(
                dataset.features[index]
                for index in training_indices
            )
            train_targets = tuple(
                dataset.targets[index]
                for index in training_indices
            )

            validation_features = tuple(
                dataset.features[index]
                for index in validation_indices
            )
            validation_targets = tuple(
                dataset.targets[index]
                for index in validation_indices
            )

            self._fit(
                model,
                train_features,
                train_targets,
            )

            predictions = self._predict(
                model,
                validation_features,
            )

            metrics = calculate_regression_metrics(
                validation_targets,
                predictions,
            )

            results.append(
                RegressionFoldResult(
                    fold=fold_number,
                    metrics=metrics,
                    sample_count=len(validation_indices),
                )
            )

        return RegressionCrossValidationResult(
            folds=tuple(results),
            mean_mae=self._mean(
                result.metrics.mae
                for result in results
            ),
            mean_rmse=self._mean(
                result.metrics.rmse
                for result in results
            ),
            mean_r2=self._mean(
                result.metrics.r2
                for result in results
            ),
        )

    def classification(
        self,
        dataset: DatasetSplit,
        estimator: object,
    ) -> ClassificationCrossValidationResult:
        """Run deterministic k-fold classification validation."""

        self._validate_dataset(dataset)

        fold_indices = self._build_folds(
            dataset.sample_count
        )

        results: list[ClassificationFoldResult] = []

        for fold_number, validation_indices in enumerate(
            fold_indices,
            start=1,
        ):
            training_indices = tuple(
                index
                for index in range(dataset.sample_count)
                if index not in validation_indices
            )

            if not training_indices:
                raise CrossValidationError(
                    "A training fold cannot be empty."
                )

            model = self._clone_estimator(
                estimator
            )

            train_features = tuple(
                dataset.features[index]
                for index in training_indices
            )
            train_targets = tuple(
                dataset.targets[index]
                for index in training_indices
            )

            validation_features = tuple(
                dataset.features[index]
                for index in validation_indices
            )
            validation_targets = tuple(
                dataset.targets[index]
                for index in validation_indices
            )

            self._fit(
                model,
                train_features,
                train_targets,
            )

            predictions = self._predict(
                model,
                validation_features,
            )

            metrics = calculate_classification_metrics(
                validation_targets,
                predictions,
            )

            results.append(
                ClassificationFoldResult(
                    fold=fold_number,
                    metrics=metrics,
                    sample_count=len(validation_indices),
                )
            )

        return ClassificationCrossValidationResult(
            folds=tuple(results),
            mean_accuracy=self._mean(
                result.metrics.accuracy
                for result in results
            ),
            mean_precision=self._mean(
                result.metrics.precision
                for result in results
            ),
            mean_recall=self._mean(
                result.metrics.recall
                for result in results
            ),
            mean_f1=self._mean(
                result.metrics.f1
                for result in results
            ),
        )

    def _build_folds(
        self,
        sample_count: int,
    ) -> tuple[tuple[int, ...], ...]:
        """Create deterministic contiguous folds."""

        if sample_count < self._folds:
            raise CrossValidationError(
                "Dataset must contain at least as many samples "
                "as the requested number of folds."
            )

        base_size, remainder = divmod(
            sample_count,
            self._folds,
        )

        folds: list[tuple[int, ...]] = []
        start = 0

        for fold_number in range(self._folds):
            size = (
                base_size
                + (1 if fold_number < remainder else 0)
            )

            end = start + size

            folds.append(
                tuple(range(start, end))
            )

            start = end

        return tuple(folds)

    @staticmethod
    def _clone_estimator(
        estimator: object,
    ) -> object:
        """Create an independent estimator for each fold."""

        try:
            from copy import deepcopy

            return deepcopy(estimator)
        except Exception as exc:
            raise CrossValidationError(
                "Estimator could not be cloned for cross-validation."
            ) from exc

    @staticmethod
    def _fit(
        estimator: object,
        features: Sequence[Sequence[float]],
        targets: Sequence[float],
    ) -> None:
        if not hasattr(estimator, "fit"):
            raise CrossValidationError(
                "Estimator must expose fit()."
            )

        try:
            estimator.fit(
                features,
                targets,
            )
        except Exception as exc:
            raise CrossValidationError(
                "Estimator fitting failed."
            ) from exc

    @staticmethod
    def _predict(
        estimator: object,
        features: Sequence[Sequence[float]],
    ) -> tuple[float, ...]:
        if not hasattr(estimator, "predict"):
            raise CrossValidationError(
                "Estimator must expose predict()."
            )

        try:
            raw_predictions = estimator.predict(
                features
            )

            if hasattr(raw_predictions, "tolist"):
                raw_predictions = raw_predictions.tolist()

            predictions = tuple(
                float(value)
                for value in raw_predictions
            )
        except (TypeError, ValueError) as exc:
            raise CrossValidationError(
                "Estimator returned invalid predictions."
            ) from exc
        except Exception as exc:
            raise CrossValidationError(
                "Estimator prediction failed."
            ) from exc

        if not predictions:
            raise CrossValidationError(
                "Estimator returned no predictions."
            )

        if not all(
            isfinite(value)
            for value in predictions
        ):
            raise CrossValidationError(
                "Estimator returned non-finite predictions."
            )

        return predictions

    @staticmethod
    def _mean(
        values: Sequence[float] | object,
    ) -> float:
        values_tuple = tuple(
            float(value)
            for value in values  # type: ignore[union-attr]
        )

        if not values_tuple:
            raise CrossValidationError(
                "Cannot calculate mean of empty results."
            )

        return round(
            sum(values_tuple) / len(values_tuple),
            6,
        )

    @staticmethod
    def _validate_dataset(
        dataset: DatasetSplit,
    ) -> None:
        if dataset.sample_count == 0:
            raise DatasetValidationError(
                "Cross-validation dataset cannot be empty."
            )


__all__ = [
    "ClassificationCrossValidationResult",
    "ClassificationFoldResult",
    "CrossValidationError",
    "CrossValidator",
    "RegressionCrossValidationResult",
    "RegressionFoldResult",
]