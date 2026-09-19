from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from krishimitra_ml.common.features import FeatureBuilder, FeatureVector


@dataclass(frozen=True, slots=True)
class IrrigationFeatureInput:
    """
    Input variables used for irrigation and crop-water prediction.

    Values should represent the current farm/crop state and the
    latest available weather information.
    """

    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_mps: float
    soil_moisture_percent: float
    crop_age_days: float
    crop_coefficient: float
    reference_et_mm: float
    previous_irrigation_mm: float = 0.0
    forecast_rainfall_mm: float = 0.0


class IrrigationFeatureBuilder:
    """Builds a deterministic feature vector for irrigation models."""

    FEATURE_NAMES: tuple[str, ...] = (
        "temperature_c",
        "humidity_percent",
        "rainfall_mm",
        "wind_speed_mps",
        "soil_moisture_percent",
        "crop_age_days",
        "crop_coefficient",
        "reference_et_mm",
        "previous_irrigation_mm",
        "forecast_rainfall_mm",
    )

    def build(
        self,
        inputs: IrrigationFeatureInput,
    ) -> FeatureVector:
        """Convert irrigation inputs into an ordered feature vector."""

        self._validate(inputs)

        values = (
            inputs.temperature_c,
            inputs.humidity_percent,
            inputs.rainfall_mm,
            inputs.wind_speed_mps,
            inputs.soil_moisture_percent,
            inputs.crop_age_days,
            inputs.crop_coefficient,
            inputs.reference_et_mm,
            inputs.previous_irrigation_mm,
            inputs.forecast_rainfall_mm,
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
        inputs: IrrigationFeatureInput,
    ) -> None:
        """Validate physical and domain constraints."""

        values = (
            inputs.temperature_c,
            inputs.humidity_percent,
            inputs.rainfall_mm,
            inputs.wind_speed_mps,
            inputs.soil_moisture_percent,
            inputs.crop_age_days,
            inputs.crop_coefficient,
            inputs.reference_et_mm,
            inputs.previous_irrigation_mm,
            inputs.forecast_rainfall_mm,
        )

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "All irrigation feature values must be finite."
            )

        if not 0.0 <= inputs.humidity_percent <= 100.0:
            raise ValueError(
                "humidity_percent must be between 0 and 100."
            )

        if not 0.0 <= inputs.soil_moisture_percent <= 100.0:
            raise ValueError(
                "soil_moisture_percent must be between 0 and 100."
            )

        if inputs.rainfall_mm < 0.0:
            raise ValueError(
                "rainfall_mm cannot be negative."
            )

        if inputs.forecast_rainfall_mm < 0.0:
            raise ValueError(
                "forecast_rainfall_mm cannot be negative."
            )

        if inputs.wind_speed_mps < 0.0:
            raise ValueError(
                "wind_speed_mps cannot be negative."
            )

        if inputs.crop_age_days < 0.0:
            raise ValueError(
                "crop_age_days cannot be negative."
            )

        if inputs.crop_coefficient <= 0.0:
            raise ValueError(
                "crop_coefficient must be greater than zero."
            )

        if inputs.reference_et_mm < 0.0:
            raise ValueError(
                "reference_et_mm cannot be negative."
            )

        if inputs.previous_irrigation_mm < 0.0:
            raise ValueError(
                "previous_irrigation_mm cannot be negative."
            )


def build_irrigation_features(
    inputs: IrrigationFeatureInput,
) -> FeatureVector:
    """Convenience function for building irrigation features."""

    return IrrigationFeatureBuilder().build(inputs)


__all__ = [
    "IrrigationFeatureBuilder",
    "IrrigationFeatureInput",
    "build_irrigation_features",
]