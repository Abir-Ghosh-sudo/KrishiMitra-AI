from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class Feature:
    """A single named model feature."""

    name: str
    value: float

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError("Feature name cannot be empty.")

        if not isfinite(self.value):
            raise ValueError(
                f"Feature '{normalized_name}' must contain a finite value."
            )


@dataclass(frozen=True, slots=True)
class FeatureVector:
    """Immutable, ordered feature vector for model inference."""

    names: tuple[str, ...]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.names:
            raise ValueError("FeatureVector cannot be empty.")

        if len(self.names) != len(self.values):
            raise ValueError(
                "Feature names and values must have the same length."
            )

        normalized_names = tuple(
            name.strip()
            for name in self.names
        )

        if any(not name for name in normalized_names):
            raise ValueError("Feature names cannot be empty.")

        if len(set(normalized_names)) != len(normalized_names):
            raise ValueError("Feature names must be unique.")

        if any(not isfinite(value) for value in self.values):
            raise ValueError(
                "FeatureVector values must all be finite."
            )

        object.__setattr__(
            self,
            "names",
            normalized_names,
        )

    @property
    def size(self) -> int:
        """Return the number of features."""

        return len(self.values)

    def as_mapping(self) -> dict[str, float]:
        """Return feature names mapped to their values."""

        return dict(zip(self.names, self.values, strict=True))

    def as_tuple(self) -> tuple[float, ...]:
        """Return the ordered numeric values."""

        return self.values


class FeatureBuilder:
    """Build deterministic feature vectors from structured inputs."""

    def __init__(self) -> None:
        self._features: dict[str, float] = {}

    def add(
        self,
        name: str,
        value: float,
    ) -> "FeatureBuilder":
        """Add or replace a numeric feature."""

        feature = Feature(
            name=name,
            value=float(value),
        )

        self._features[feature.name.strip()] = feature.value
        return self

    def add_optional(
        self,
        name: str,
        value: float | None,
    ) -> "FeatureBuilder":
        """Add a feature only when a value is available."""

        if value is not None:
            self.add(name, value)

        return self

    def add_many(
        self,
        features: Mapping[str, float],
    ) -> "FeatureBuilder":
        """Add multiple named features."""

        for name, value in features.items():
            self.add(name, value)

        return self

    def build(
        self,
        *,
        names: Iterable[str] | None = None,
    ) -> FeatureVector:
        """
        Build an immutable feature vector.

        When names are supplied, that order is used and every requested
        feature must exist. Otherwise insertion order is preserved.
        """

        if names is None:
            ordered_names = tuple(self._features.keys())
        else:
            ordered_names = tuple(
                name.strip()
                for name in names
            )

            if not ordered_names:
                raise ValueError(
                    "Feature name ordering cannot be empty."
                )

            missing = [
                name
                for name in ordered_names
                if name not in self._features
            ]

            if missing:
                raise KeyError(
                    "Missing features: "
                    + ", ".join(missing)
                )

            if len(set(ordered_names)) != len(ordered_names):
                raise ValueError(
                    "Feature names must be unique."
                )

        if not ordered_names:
            raise ValueError(
                "Cannot build an empty feature vector."
            )

        return FeatureVector(
            names=ordered_names,
            values=tuple(
                self._features[name]
                for name in ordered_names
            ),
        )


def build_feature_vector(
    features: Mapping[str, float],
    *,
    names: Iterable[str] | None = None,
) -> FeatureVector:
    """Create a feature vector from a mapping."""

    builder = FeatureBuilder()
    builder.add_many(features)
    return builder.build(names=names)