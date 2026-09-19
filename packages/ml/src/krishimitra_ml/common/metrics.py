from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Sequence


@dataclass(frozen=True, slots=True)
class RegressionMetrics:
    """Standard regression evaluation metrics."""

    mae: float
    mse: float
    rmse: float
    r2: float

    def __post_init__(self) -> None:
        for name, value in (
            ("mae", self.mae),
            ("mse", self.mse),
            ("rmse", self.rmse),
            ("r2", self.r2),
        ):
            if not isfinite(value):
                raise ValueError(
                    f"{name} must be finite."
                )

        if self.mae < 0:
            raise ValueError("mae cannot be negative.")

        if self.mse < 0:
            raise ValueError("mse cannot be negative.")

        if self.rmse < 0:
            raise ValueError("rmse cannot be negative.")


@dataclass(frozen=True, slots=True)
class ClassificationMetrics:
    """Standard binary/multiclass classification metrics."""

    accuracy: float
    precision: float
    recall: float
    f1: float

    def __post_init__(self) -> None:
        for name, value in (
            ("accuracy", self.accuracy),
            ("precision", self.precision),
            ("recall", self.recall),
            ("f1", self.f1),
        ):
            if not isfinite(value):
                raise ValueError(
                    f"{name} must be finite."
                )

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0 and 1."
                )


def mean_absolute_error(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """Calculate mean absolute error."""

    _validate_regression_inputs(y_true, y_pred)

    return sum(
        abs(actual - predicted)
        for actual, predicted in zip(
            y_true,
            y_pred,
            strict=True,
        )
    ) / len(y_true)


def mean_squared_error(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """Calculate mean squared error."""

    _validate_regression_inputs(y_true, y_pred)

    return sum(
        (actual - predicted) ** 2
        for actual, predicted in zip(
            y_true,
            y_pred,
            strict=True,
        )
    ) / len(y_true)


def root_mean_squared_error(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """Calculate root mean squared error."""

    return sqrt(
        mean_squared_error(
            y_true,
            y_pred,
        )
    )


def r2_score(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """Calculate the coefficient of determination."""

    _validate_regression_inputs(y_true, y_pred)

    mean_true = sum(y_true) / len(y_true)

    total_sum_of_squares = sum(
        (actual - mean_true) ** 2
        for actual in y_true
    )

    if total_sum_of_squares == 0:
        if all(
            actual == predicted
            for actual, predicted in zip(
                y_true,
                y_pred,
                strict=True,
            )
        ):
            return 1.0

        return 0.0

    residual_sum_of_squares = sum(
        (actual - predicted) ** 2
        for actual, predicted in zip(
            y_true,
            y_pred,
            strict=True,
        )
    )

    return (
        1.0
        - residual_sum_of_squares
        / total_sum_of_squares
    )


def calculate_regression_metrics(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> RegressionMetrics:
    """Calculate the complete regression metric set."""

    mae = mean_absolute_error(
        y_true,
        y_pred,
    )
    mse = mean_squared_error(
        y_true,
        y_pred,
    )

    return RegressionMetrics(
        mae=mae,
        mse=mse,
        rmse=sqrt(mse),
        r2=r2_score(
            y_true,
            y_pred,
        ),
    )


def accuracy_score(
    y_true: Sequence[object],
    y_pred: Sequence[object],
) -> float:
    """Calculate classification accuracy."""

    _validate_classification_inputs(
        y_true,
        y_pred,
    )

    correct = sum(
        actual == predicted
        for actual, predicted in zip(
            y_true,
            y_pred,
            strict=True,
        )
    )

    return correct / len(y_true)


def precision_score(
    y_true: Sequence[object],
    y_pred: Sequence[object],
    *,
    positive_label: object = 1,
) -> float:
    """Calculate binary precision for the selected positive class."""

    _validate_classification_inputs(
        y_true,
        y_pred,
    )

    true_positive = 0
    false_positive = 0

    for actual, predicted in zip(
        y_true,
        y_pred,
        strict=True,
    ):
        if predicted == positive_label:
            if actual == positive_label:
                true_positive += 1
            else:
                false_positive += 1

    denominator = true_positive + false_positive

    if denominator == 0:
        return 0.0

    return true_positive / denominator


def recall_score(
    y_true: Sequence[object],
    y_pred: Sequence[object],
    *,
    positive_label: object = 1,
) -> float:
    """Calculate binary recall for the selected positive class."""

    _validate_classification_inputs(
        y_true,
        y_pred,
    )

    true_positive = 0
    false_negative = 0

    for actual, predicted in zip(
        y_true,
        y_pred,
        strict=True,
    ):
        if actual == positive_label:
            if predicted == positive_label:
                true_positive += 1
            else:
                false_negative += 1

    denominator = true_positive + false_negative

    if denominator == 0:
        return 0.0

    return true_positive / denominator


def f1_score(
    y_true: Sequence[object],
    y_pred: Sequence[object],
    *,
    positive_label: object = 1,
) -> float:
    """Calculate binary F1 score."""

    precision = precision_score(
        y_true,
        y_pred,
        positive_label=positive_label,
    )
    recall = recall_score(
        y_true,
        y_pred,
        positive_label=positive_label,
    )

    denominator = precision + recall

    if denominator == 0:
        return 0.0

    return (
        2.0 * precision * recall
        / denominator
    )


def calculate_classification_metrics(
    y_true: Sequence[object],
    y_pred: Sequence[object],
    *,
    positive_label: object = 1,
) -> ClassificationMetrics:
    """Calculate the complete binary classification metric set."""

    return ClassificationMetrics(
        accuracy=accuracy_score(
            y_true,
            y_pred,
        ),
        precision=precision_score(
            y_true,
            y_pred,
            positive_label=positive_label,
        ),
        recall=recall_score(
            y_true,
            y_pred,
            positive_label=positive_label,
        ),
        f1=f1_score(
            y_true,
            y_pred,
            positive_label=positive_label,
        ),
    )


def _validate_regression_inputs(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> None:
    """Validate regression metric inputs."""

    if not y_true:
        raise ValueError(
            "y_true cannot be empty."
        )

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must have the same length."
        )

    for index, value in enumerate(y_true):
        if not isfinite(value):
            raise ValueError(
                f"y_true[{index}] must be finite."
            )

    for index, value in enumerate(y_pred):
        if not isfinite(value):
            raise ValueError(
                f"y_pred[{index}] must be finite."
            )


def _validate_classification_inputs(
    y_true: Sequence[object],
    y_pred: Sequence[object],
) -> None:
    """Validate classification metric inputs."""

    if not y_true:
        raise ValueError(
            "y_true cannot be empty."
        )

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must have the same length."
        )