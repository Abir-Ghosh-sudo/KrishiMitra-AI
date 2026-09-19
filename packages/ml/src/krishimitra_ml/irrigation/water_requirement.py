from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class WaterRequirementResult:
    """Crop water requirement calculation result."""

    crop_evapotranspiration_mm: float
    effective_rainfall_mm: float
    net_irrigation_requirement_mm: float
    gross_irrigation_requirement_mm: float
    water_deficit_mm: float


class WaterRequirementCalculator:
    """
    Calculates crop-water and irrigation requirements.

    The calculation is deterministic and physics/agronomy based.
    It does not use an LLM and does not invent irrigation quantities.
    """

    def __init__(
        self,
        *,
        irrigation_efficiency: float = 0.85,
        rainfall_effectiveness: float = 0.70,
    ) -> None:
        if not 0.0 < irrigation_efficiency <= 1.0:
            raise ValueError(
                "irrigation_efficiency must be greater than 0 "
                "and at most 1."
            )

        if not 0.0 <= rainfall_effectiveness <= 1.0:
            raise ValueError(
                "rainfall_effectiveness must be between 0 and 1."
            )

        self._irrigation_efficiency = irrigation_efficiency
        self._rainfall_effectiveness = rainfall_effectiveness

    def calculate(
        self,
        *,
        reference_et_mm: float,
        crop_coefficient: float,
        rainfall_mm: float = 0.0,
        soil_water_available_mm: float = 0.0,
        previous_irrigation_mm: float = 0.0,
    ) -> WaterRequirementResult:
        """
        Calculate the irrigation requirement for the current period.

        ETc = ET0 × Kc

        Net irrigation requirement is based on crop water demand
        minus effective rainfall, available soil water, and the
        previous irrigation contribution.
        """

        self._validate(
            reference_et_mm=reference_et_mm,
            crop_coefficient=crop_coefficient,
            rainfall_mm=rainfall_mm,
            soil_water_available_mm=soil_water_available_mm,
            previous_irrigation_mm=previous_irrigation_mm,
        )

        crop_evapotranspiration = (
            reference_et_mm * crop_coefficient
        )

        effective_rainfall = (
            rainfall_mm * self._rainfall_effectiveness
        )

        available_water = (
            effective_rainfall
            + soil_water_available_mm
            + previous_irrigation_mm
        )

        water_deficit = max(
            0.0,
            crop_evapotranspiration - available_water,
        )

        net_irrigation_requirement = water_deficit

        gross_irrigation_requirement = (
            net_irrigation_requirement
            / self._irrigation_efficiency
        )

        return WaterRequirementResult(
            crop_evapotranspiration_mm=round(
                crop_evapotranspiration,
                4,
            ),
            effective_rainfall_mm=round(
                effective_rainfall,
                4,
            ),
            net_irrigation_requirement_mm=round(
                net_irrigation_requirement,
                4,
            ),
            gross_irrigation_requirement_mm=round(
                gross_irrigation_requirement,
                4,
            ),
            water_deficit_mm=round(
                water_deficit,
                4,
            ),
        )

    @staticmethod
    def _validate(
        *,
        reference_et_mm: float,
        crop_coefficient: float,
        rainfall_mm: float,
        soil_water_available_mm: float,
        previous_irrigation_mm: float,
    ) -> None:
        values = (
            reference_et_mm,
            crop_coefficient,
            rainfall_mm,
            soil_water_available_mm,
            previous_irrigation_mm,
        )

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "All water requirement inputs must be finite."
            )

        if reference_et_mm < 0.0:
            raise ValueError(
                "reference_et_mm cannot be negative."
            )

        if crop_coefficient <= 0.0:
            raise ValueError(
                "crop_coefficient must be greater than zero."
            )

        if rainfall_mm < 0.0:
            raise ValueError(
                "rainfall_mm cannot be negative."
            )

        if soil_water_available_mm < 0.0:
            raise ValueError(
                "soil_water_available_mm cannot be negative."
            )

        if previous_irrigation_mm < 0.0:
            raise ValueError(
                "previous_irrigation_mm cannot be negative."
            )


def calculate_water_requirement(
    *,
    reference_et_mm: float,
    crop_coefficient: float,
    rainfall_mm: float = 0.0,
    soil_water_available_mm: float = 0.0,
    previous_irrigation_mm: float = 0.0,
    irrigation_efficiency: float = 0.85,
    rainfall_effectiveness: float = 0.70,
) -> WaterRequirementResult:
    """Convenience wrapper for water requirement calculation."""

    calculator = WaterRequirementCalculator(
        irrigation_efficiency=irrigation_efficiency,
        rainfall_effectiveness=rainfall_effectiveness,
    )

    return calculator.calculate(
        reference_et_mm=reference_et_mm,
        crop_coefficient=crop_coefficient,
        rainfall_mm=rainfall_mm,
        soil_water_available_mm=soil_water_available_mm,
        previous_irrigation_mm=previous_irrigation_mm,
    )


__all__ = [
    "WaterRequirementCalculator",
    "WaterRequirementResult",
    "calculate_water_requirement",
]