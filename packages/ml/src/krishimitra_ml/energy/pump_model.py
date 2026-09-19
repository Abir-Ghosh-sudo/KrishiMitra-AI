from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class PumpOperatingPoint:
    """Hydraulic operating point of an irrigation pump."""

    flow_rate_liters_per_minute: float
    head_m: float
    pump_efficiency: float


@dataclass(frozen=True, slots=True)
class PumpPowerResult:
    """Estimated pump hydraulic and electrical power."""

    hydraulic_power_kw: float
    electrical_power_kw: float
    estimated_efficiency: float


class PumpModel:
    """
    Deterministic pump power model.

    Hydraulic power:

        P_h = rho × g × Q × H

    Electrical input power accounts for pump efficiency.

    This model deliberately requires the pump operating point instead
    of inventing pump specifications.
    """

    WATER_DENSITY_KG_M3 = 1000.0
    GRAVITY_M_S2 = 9.80665

    def calculate_power(
        self,
        operating_point: PumpOperatingPoint,
    ) -> PumpPowerResult:
        """Calculate hydraulic and electrical pump power."""

        self._validate(operating_point)

        flow_rate_m3_per_second = (
            operating_point.flow_rate_liters_per_minute
            / 1000.0
            / 60.0
        )

        hydraulic_power_watts = (
            self.WATER_DENSITY_KG_M3
            * self.GRAVITY_M_S2
            * flow_rate_m3_per_second
            * operating_point.head_m
        )

        hydraulic_power_kw = (
            hydraulic_power_watts / 1000.0
        )

        electrical_power_kw = (
            hydraulic_power_kw
            / operating_point.pump_efficiency
        )

        return PumpPowerResult(
            hydraulic_power_kw=round(
                hydraulic_power_kw,
                6,
            ),
            electrical_power_kw=round(
                electrical_power_kw,
                6,
            ),
            estimated_efficiency=round(
                operating_point.pump_efficiency,
                6,
            ),
        )

    @staticmethod
    def _validate(
        operating_point: PumpOperatingPoint,
    ) -> None:
        values = (
            operating_point.flow_rate_liters_per_minute,
            operating_point.head_m,
            operating_point.pump_efficiency,
        )

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "Pump operating-point values must be finite."
            )

        if operating_point.flow_rate_liters_per_minute < 0.0:
            raise ValueError(
                "flow_rate_liters_per_minute cannot be negative."
            )

        if operating_point.head_m < 0.0:
            raise ValueError(
                "head_m cannot be negative."
            )

        if not 0.0 < operating_point.pump_efficiency <= 1.0:
            raise ValueError(
                "pump_efficiency must be greater than 0 and at most 1."
            )


__all__ = [
    "PumpModel",
    "PumpOperatingPoint",
    "PumpPowerResult",
]