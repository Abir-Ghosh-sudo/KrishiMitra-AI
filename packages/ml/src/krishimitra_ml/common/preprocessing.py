from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Sequence

from .features import FeatureVector


@dataclass(frozen=True, slots=True)
class FeatureStatistics:
    """Statistics required for deterministic feature normalization."""

    means: tuple[float, ...]
    standard_deviations: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.means) != len(self.standard_deviations):
            raise ValueError(
                "Means and standard deviations must have the same length."
            )

        if not self.means:
            raise ValueError(
                "Feature statistics cannot be empty."
            )

        for index, (mean, std) in enumerate(
            zip(
                self.means,
                self.standard_deviations,
                strict=True,
            )
        ):
            if not isfinite(mean):
                raise ValueError(
                    f"Mean at index {index} must be finite."
                )

            if not isfinite(std) or std < 0:
                raise ValueError(
                    f"Standard deviation at index {index} "
                    "must be finite and non-negative."
                )


@dataclass(frozen=True, slots=True)
class PreprocessedFeatures:
    """Result of a preprocessing operation."""

    feature_vector: FeatureVector
    statistics: FeatureStatistics | None = None


class FeaturePreprocessor:
    """
    Deterministic preprocessing for tabular ML features.

    The class deliberately avoids silently changing feature semantics.
    Missing values must be handled explicitly through the configured
    strategy, and feature ordering is preserved.
    """

    def __init__(
        self,
        *,
        missing_value: float | None = None,
        standardize: bool = False,
    ) -> None:
        if missing_value is not None and not isfinite(missing_value):
            raise ValueError(
                "missing_value must be finite when provided."
            )

        self._missing_value = missing_value
        self._standardize = standardize
        self._statistics: FeatureStatistics | None = None

    @property
    def statistics(self) -> FeatureStatistics | None:
        """Return fitted normalization statistics."""

        return self._statistics

    def fit(
        self,
        rows: Sequence[FeatureVector],
    ) -> "FeaturePreprocessor":
        """Fit normalization statistics from training feature vectors."""

        if not rows:
            raise ValueError(
                "At least one feature vector is required for fitting."
            )

        first = rows[0]
        feature_names = first.names

        for row in rows[1:]:
            if row.names != feature_names:
                raise ValueError(
                    "All feature vectors must use the same feature ordering."
                )

        if not self._standardize:
            self._statistics = None
            return self

        means: list[float] = []
        standard_deviations: list[float] = []

        for index in range(first.size):
            values = [
                self._resolve_missing(row.values[index])
                for row in rows
            ]

            mean = sum(values) / len(values)

            variance = sum(
                (value - mean) ** 2
                for value in values
            ) / len(values)

            standard_deviations.append(
                variance ** 0.5
            )
            means.append(mean)

        self._statistics = FeatureStatistics(
            means=tuple(means),
            standard_deviations=tuple(standard_deviations),
        )

        return self

    def transform(
        self,
        features: FeatureVector,
    ) -> FeatureVector:
        """Transform a feature vector using fitted preprocessing rules."""

        values = [
            self._resolve_missing(value)
            for value in features.values
        ]

        if self._standardize:
            if self._statistics is None:
                raise RuntimeError(
                    "FeaturePreprocessor must be fitted before "
                    "standardization."
                )

            values = [
                self._standardize_value(
                    value=value,
                    mean=mean,
                    standard_deviation=standard_deviation,
                )
                for value, mean, standard_deviation in zip(
                    values,
                    self._statistics.means,
                    self._statistics.standard_deviations,
                    strict=True,
                )
            ]

        return FeatureVector(
            names=features.names,
            values=tuple(values),
        )

    def fit_transform(
        self,
        rows: Sequence[FeatureVector],
    ) -> tuple[FeatureVector, ...]:
        """Fit the preprocessor and transform the supplied rows."""

        self.fit(rows)

        return tuple(
            self.transform(row)
            for row in rows
        )

    def _resolve_missing(
        self,
        value: float,
    ) -> float:
        """Resolve non-finite values according to the configured policy."""

        if isfinite(value):
            return value

        if self._missing_value is None:
            raise ValueError(
                "Encountered a non-finite feature value and no "
                "missing_value strategy was configured."
            )

        return self._missing_value

    @staticmethod
    def _standardize_value(
        *,
        value: float,
        mean: float,
        standard_deviation: float,
    ) -> float:
        """Standardize one value using fitted statistics."""

        if standard_deviation == 0:
            return 0.0

        return (
            value - mean
        ) / standard_deviation


def ensure_feature_order(
    features: FeatureVector,
    expected_names: Iterable[str],
) -> FeatureVector:
    """
    Reorder a feature vector to a model's expected feature order.

    Raises an error when the model expects a feature that is unavailable.
    """

    names = tuple(
        name.strip()
        for name in expected_names
    )

    if not names:
        raise ValueError(
            "Expected feature names cannot be empty."
        )

    mapping = features.as_mapping()

    missing = [
        name
        for name in names
        if name not in mapping
    ]

    if missing:
        raise KeyError(
            "Missing required features: "
            + ", ".join(missing)
        )

    return FeatureVector(
        names=names,
        values=tuple(
            mapping[name]
            for name in names
        ),
    )