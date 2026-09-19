from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from krishimitra_ml.common.features import FeatureBuilder, FeatureVector


@dataclass(frozen=True, slots=True)
class YieldFeatureInput:
    """Input variables used for crop-yield prediction."""

    temperature_mean_c: float
    temperature_min_c: float
    temperature_max_c: float
    rainfall_mm: float
    humidity_percent: float
    crop_age_days: float
    crop_area_hectares: float
    soil_moisture_percent: float
    soil_nitrogen: float
    soil_phosphorus: float
    soil_potassium: float
    soil_ph: float
    irrigation_mm: float
    fertilizer_kg_per_hectare: float
    disease_pressure: float = 0.0
    pest_pressure: float = 0.0


class YieldFeatureBuilder:
    """Build a deterministic feature vector for yield models."""

    FEATURE_NAMES: tuple[str, ...] = (
        "temperature_mean_c",
        "temperature_min_c",
        "temperature_max_c",
        "rainfall_mm",
        "humidity_percent",
        "crop_age_days",
        "crop_area_hectares",
        "soil_moisture_percent",
        "soil_nitrogen",
        "soil_phosphorus",
        "soil_potassium",
        "soil_ph",
        "irrigation_mm",
        "fertilizer_kg_per_hectare",
        "disease_pressure",
        "pest_pressure",
    )

    def build(
        self,
        inputs: YieldFeatureInput,
    ) -> FeatureVector:
        """Convert yield inputs into an ordered feature vector."""

        self._validate(inputs)

        values = (
            inputs.temperature_mean_c,
            inputs.temperature_min_c,
            inputs.temperature_max_c,
            inputs.rainfall_mm,
            inputs.humidity_percent,
            inputs.crop_age_days,
            inputs.crop_area_hectares,
            inputs.soil_moisture_percent,
            inputs.soil_nitrogen,
            inputs.soil_phosphorus,
            inputs.soil_potassium,
            inputs.soil_ph,
            inputs.irrigation_mm,
            inputs.fertilizer_kg_per_hectare,
            inputs.disease_pressure,
            inputs.pest_pressure,
        )

        builder = FeatureBuilder()

        for name, value in zip(
            self.FEATURE_NAMES,
            values,
            strict=True,
        ):
            builder.add(
                name=name,
                value=value,
            )

        return builder.build()

    @staticmethod
    def _validate(
        inputs: YieldFeatureInput,
    ) -> None:
        values = (
            inputs.temperature_mean_c,
            inputs.temperature_min_c,
            inputs.temperature_max_c,
            inputs.rainfall_mm,
            inputs.humidity_percent,
            inputs.crop_age_days,
            inputs.crop_area_hectares,
            inputs.soil_moisture_percent,
            inputs.soil_nitrogen,
            inputs.soil_phosphorus,
            inputs.soil_potassium,
            inputs.soil_ph,
            inputs.irrigation_mm,
            inputs.fertilizer_kg_per_hectare,
            inputs.disease_pressure,
            inputs.pest_pressure,
        )

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "All yield feature values must be finite."
            )

        if inputs.temperature_min_c > inputs.temperature_max_c:
            raise ValueError(
                "temperature_min_c cannot exceed "
                "temperature_max_c."
            )

        if not (
            inputs.temperature_min_c
            <= inputs.temperature_mean_c
            <= inputs.temperature_max_c
        ):
            raise ValueError(
                "temperature_mean_c must be between "
                "temperature_min_c and temperature_max_c."
            )

        if inputs.rainfall_mm < 0.0:
            raise ValueError(
                "rainfall_mm cannot be negative."
            )

        if not 0.0 <= inputs.humidity_percent <= 100.0:
            raise ValueError(
                "humidity_percent must be between 0 and 100."
            )

        if inputs.crop_age_days < 0.0:
            raise ValueError(
                "crop_age_days cannot be negative."
            )

        if inputs.crop_area_hectares <= 0.0:
            raise ValueError(
                "crop_area_hectares must be greater than zero."
            )

        if not 0.0 <= inputs.soil_moisture_percent <= 100.0:
            raise ValueError(
                "soil_moisture_percent must be between 0 and 100."
            )

        if inputs.soil_nitrogen < 0.0:
            raise ValueError(
                "soil_nitrogen cannot be negative."
            )

        if inputs.soil_phosphorus < 0.0:
            raise ValueError(
                "soil_phosphorus cannot be negative."
            )

        if inputs.soil_potassium < 0.0:
            raise ValueError(
                "soil_potassium cannot be negative."
            )

        if not 0.0 < inputs.soil_ph <= 14.0:
            raise ValueError(
                "soil_ph must be greater than 0 and at most 14."
            )

        if inputs.irrigation_mm < 0.0:
            raise ValueError(
                "irrigation_mm cannot be negative."
            )

        if inputs.fertilizer_kg_per_hectare < 0.0:
            raise ValueError(
                "fertilizer_kg_per_hectare cannot be negative."
            )

        if not 0.0 <= inputs.disease_pressure <= 1.0:
            raise ValueError(
                "disease_pressure must be between 0 and 1."
            )

        if not 0.0 <= inputs.pest_pressure <= 1.0:
            raise ValueError(
                "pest_pressure must be between 0 and 1."
            )


def build_yield_features(
    inputs: YieldFeatureInput,
) -> FeatureVector:
    """Convenience function for building yield features."""

    return YieldFeatureBuilder().build(inputs)


__all__ = [
    "YieldFeatureBuilder",
    "YieldFeatureInput",
    "build_yield_features",
]