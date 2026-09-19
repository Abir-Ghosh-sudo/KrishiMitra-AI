from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from krishimitra_ml.common.features import (
    FeatureBuilder,
    FeatureVector,
)


@dataclass(frozen=True, slots=True)
class PestFeatureInput:
    """Agricultural signals used for pest-risk prediction."""

    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    crop_age_days: float
    soil_moisture_percent: float | None = None
    irrigation_count_7d: float = 0.0
    previous_pest_incidents_30d: float = 0.0

    def to_mapping(self) -> Mapping[str, float]:
        """Convert the pest inputs into model features."""

        values = {
            "temperature_c": self.temperature_c,
            "humidity_percent": self.humidity_percent,
            "rainfall_mm": self.rainfall_mm,
            "wind_speed_kmh": self.wind_speed_kmh,
            "crop_age_days": self.crop_age_days,
            "irrigation_count_7d": self.irrigation_count_7d,
            "previous_pest_incidents_30d": (
                self.previous_pest_incidents_30d
            ),
        }

        if self.soil_moisture_percent is not None:
            values["soil_moisture_percent"] = (
                self.soil_moisture_percent
            )

        return values


class PestFeatureBuilder:
    """Build deterministic feature vectors for pest-risk models."""

    DEFAULT_FEATURE_ORDER: tuple[str, ...] = (
        "temperature_c",
        "humidity_percent",
        "rainfall_mm",
        "wind_speed_kmh",
        "crop_age_days",
        "soil_moisture_percent",
        "irrigation_count_7d",
        "previous_pest_incidents_30d",
    )

    def __init__(
        self,
        *,
        feature_order: Sequence[str] | None = None,
    ) -> None:
        order = tuple(
            feature_order
            or self.DEFAULT_FEATURE_ORDER
        )

        if not order:
            raise ValueError(
                "feature_order cannot be empty."
            )

        if len(set(order)) != len(order):
            raise ValueError(
                "feature_order must contain unique names."
            )

        if any(
            not name.strip()
            for name in order
        ):
            raise ValueError(
                "feature_order cannot contain empty names."
            )

        self._feature_order = order

    @property
    def feature_order(self) -> tuple[str, ...]:
        """Return the deterministic model feature order."""

        return self._feature_order

    def build(
        self,
        inputs: PestFeatureInput,
    ) -> FeatureVector:
        """Build a feature vector from pest-related farm signals."""

        mapping = inputs.to_mapping()

        builder = FeatureBuilder()

        for name in self._feature_order:
            if name not in mapping:
                raise ValueError(
                    f"Required pest feature is unavailable: {name}"
                )

            builder.add(
                name,
                mapping[name],
            )

        return builder.build()


def build_pest_features(
    inputs: PestFeatureInput,
    *,
    feature_order: Sequence[str] | None = None,
) -> FeatureVector:
    """Convenience function for pest feature construction."""

    return PestFeatureBuilder(
        feature_order=feature_order,
    ).build(inputs)