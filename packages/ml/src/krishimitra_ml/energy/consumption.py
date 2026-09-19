from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class EnergyConsumptionInput:
    """Inputs required to estimate irrigation energy consumption."""

    water_volume_liters: float
    total_head_m: float
    pump_efficiency: float
    motor_efficiency: float = 0.90
    operating_hours: float | None = None
    flow_rate_liters_per_minute: float | None = None


@dataclass(frozen=True, slots=True)
class EnergyConsumptionResult:
    """Estimated energy consumption."""

    hydraulic_energy_kwh: float
    electrical_energy_kwh: float
    estimated_operating_hours: float | None


class EnergyConsumptionCalculator:
    """
    Calculate the energy required to move irrigation water.

    Hydraulic energy:

        E = rho × g × V × H

    Electrical energy accounts for pump and motor efficiency.

    This calculator is deterministic and does not pretend to know
    real pump characteristics unless they are explicitly supplied.
    """

    WATER_DENSITY_KG_M3 = 1000.0
    GRAVITY_M_S2 = 9.80665
    JOULES_PER_KWH = 3_600_000.0

    def calculate(
        self,
        inputs: EnergyConsumptionInput,
    ) -> EnergyConsumptionResult:
        """Calculate hydraulic and electrical energy consumption."""

        self._validate(inputs)

        water_volume_m3 = (
            inputs.water_volume_liters / 1000.0
        )

        hydraulic_energy_joules = (
            self.WATER_DENSITY_KG_M3
            * self.GRAVITY_M_S2
            * water_volume_m3
            * inputs.total_head_m
        )

        hydraulic_energy_kwh = (
            hydraulic_energy_joules
            / self.JOULES_PER_KWH
        )

        combined_efficiency = (
            inputs.pump_efficiency
            * inputs.motor_efficiency
        )

        electrical_energy_kwh = (
            hydraulic_energy_kwh
            / combined_efficiency
        )

        operating_hours = inputs.operating_hours

        if (
            operating_hours is None
            and inputs.flow_rate_liters_per_minute is not None
        ):
            operating_hours = (
                inputs.water_volume_liters
                / inputs.flow_rate_liters_per_minute
                / 60.0
            )

        return EnergyConsumptionResult(
            hydraulic_energy_kwh=round(
                hydraulic_energy_kwh,
                6,
            ),
            electrical_energy_kwh=round(
                electrical_energy_kwh,
                6,
            ),
            estimated_operating_hours=(
                None
                if operating_hours is None
                else round(operating_hours, 6)
            ),
        )

    @staticmethod
    def _validate(
        inputs: EnergyConsumptionInput,
    ) -> None:
        values = (
            inputs.water_volume_liters,
            inputs.total_head_m,
            inputs.pump_efficiency,
            inputs.motor_efficiency,
        )

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "Energy consumption inputs must be finite."
            )

        if inputs.operating_hours is not None:
            if not isfinite(inputs.operating_hours):
                raise ValueError(
                    "operating_hours must be finite."
                )

        if inputs.flow_rate_liters_per_minute is not None:
            if not isfinite(inputs.flow_rate_liters_per_minute):
                raise ValueError(
                    "flow_rate_liters_per_minute must be finite."
                )

        if inputs.water_volume_liters < 0.0:
            raise ValueError(
                "water_volume_liters cannot be negative."
            )

        if inputs.total_head_m < 0.0:
            raise ValueError(
                "total_head_m cannot be negative."
            )

        if not 0.0 < inputs.pump_efficiency <= 1.0:
            raise ValueError(
                "pump_efficiency must be greater than 0 and at most 1."
            )

        if not 0.0 < inputs.motor_efficiency <= 1.0:
            raise ValueError(
                "motor_efficiency must be greater than 0 and at most 1."
            )

        if (
            inputs.operating_hours is not None
            and inputs.operating_hours < 0.0
        ):
            raise ValueError(
                "operating_hours cannot be negative."
            )

        if (
            inputs.flow_rate_liters_per_minute is not None
            and inputs.flow_rate_liters_per_minute < 0.0
        ):
            raise ValueError(
                "flow_rate_liters_per_minute cannot be negative."
            )

        if (
            inputs.operating_hours is None
            and inputs.flow_rate_liters_per_minute == 0.0
            and inputs.water_volume_liters > 0.0
        ):
            raise ValueError(
                "A positive water volume requires either "
                "operating_hours or a positive flow rate."
            )


def calculate_energy_consumption(
    inputs: EnergyConsumptionInput,
) -> EnergyConsumptionResult:
    """Convenience wrapper for energy consumption calculation."""

    return EnergyConsumptionCalculator().calculate(inputs)


__all__ = [
    "EnergyConsumptionCalculator",
    "EnergyConsumptionInput",
    "EnergyConsumptionResult",
    "calculate_energy_consumption",
]