from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Sequence


class DatasetValidationError(ValueError):
    """Raised when a machine-learning dataset is invalid."""


@dataclass(frozen=True, slots=True)
class DatasetSplit:
    """A deterministic train/validation/test dataset split."""

    features: tuple[tuple[float, ...], ...]
    targets: tuple[float, ...]
    feature_names: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.features) != len(self.targets):
            raise DatasetValidationError(
                "features and targets must contain the same number of rows."
            )

        if not self.feature_names:
            raise DatasetValidationError(
                "feature_names cannot be empty."
            )

        expected_width = len(self.feature_names)

        for row in self.features:
            if len(row) != expected_width:
                raise DatasetValidationError(
                    "Every feature row must match feature_names length."
                )

            if not all(isfinite(float(value)) for value in row):
                raise DatasetValidationError(
                    "Feature values must be finite."
                )

        for target in self.targets:
            if not isfinite(float(target)):
                raise DatasetValidationError(
                    "Target values must be finite."
                )

    @property
    def sample_count(self) -> int:
        """Return the number of samples."""

        return len(self.features)

    @property
    def feature_count(self) -> int:
        """Return the number of features."""

        return len(self.feature_names)


@dataclass(frozen=True, slots=True)
class DatasetBundle:
    """Complete dataset with explicit train/validation/test splits."""

    train: DatasetSplit
    validation: DatasetSplit
    test: DatasetSplit

    def __post_init__(self) -> None:
        if self.train.feature_names != self.validation.feature_names:
            raise DatasetValidationError(
                "Train and validation feature schemas must match."
            )

        if self.train.feature_names != self.test.feature_names:
            raise DatasetValidationError(
                "Train and test feature schemas must match."
            )

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return the canonical feature schema."""

        return self.train.feature_names

    @property
    def total_samples(self) -> int:
        """Return the total number of samples."""

        return (
            self.train.sample_count
            + self.validation.sample_count
            + self.test.sample_count
        )


class DatasetBuilder:
    """
    Build validated datasets from in-memory records.

    Data loading from CSV, Parquet, databases, or object storage is
    intentionally kept outside this class. This layer owns dataset
    structure and validation, not storage.
    """

    def __init__(
        self,
        feature_names: Sequence[str],
    ) -> None:
        names = tuple(
            str(name).strip()
            for name in feature_names
        )

        if not names:
            raise DatasetValidationError(
                "At least one feature name is required."
            )

        if any(not name for name in names):
            raise DatasetValidationError(
                "Feature names cannot be empty."
            )

        if len(set(names)) != len(names):
            raise DatasetValidationError(
                "Feature names must be unique."
            )

        self._feature_names = names

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return the dataset feature schema."""

        return self._feature_names

    def build_split(
        self,
        features: Iterable[Sequence[float]],
        targets: Iterable[float],
    ) -> DatasetSplit:
        """Create a validated dataset split."""

        feature_rows = tuple(
            tuple(float(value) for value in row)
            for row in features
        )

        target_values = tuple(
            float(target)
            for target in targets
        )

        return DatasetSplit(
            features=feature_rows,
            targets=target_values,
            feature_names=self._feature_names,
        )

    def build_bundle(
        self,
        *,
        train_features: Iterable[Sequence[float]],
        train_targets: Iterable[float],
        validation_features: Iterable[Sequence[float]],
        validation_targets: Iterable[float],
        test_features: Iterable[Sequence[float]],
        test_targets: Iterable[float],
    ) -> DatasetBundle:
        """Create a complete train/validation/test dataset bundle."""

        return DatasetBundle(
            train=self.build_split(
                train_features,
                train_targets,
            ),
            validation=self.build_split(
                validation_features,
                validation_targets,
            ),
            test=self.build_split(
                test_features,
                test_targets,
            ),
        )


def build_dataset_bundle(
    *,
    feature_names: Sequence[str],
    train_features: Iterable[Sequence[float]],
    train_targets: Iterable[float],
    validation_features: Iterable[Sequence[float]],
    validation_targets: Iterable[float],
    test_features: Iterable[Sequence[float]],
    test_targets: Iterable[float],
) -> DatasetBundle:
    """Convenience function for constructing a validated dataset."""

    return DatasetBuilder(
        feature_names
    ).build_bundle(
        train_features=train_features,
        train_targets=train_targets,
        validation_features=validation_features,
        validation_targets=validation_targets,
        test_features=test_features,
        test_targets=test_targets,
    )


__all__ = [
    "DatasetBuilder",
    "DatasetBundle",
    "DatasetSplit",
    "DatasetValidationError",
    "build_dataset_bundle",
]