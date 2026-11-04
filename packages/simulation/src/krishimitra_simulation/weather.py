from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class WeatherScenario:
    name: str
    temp_delta_c: float
    rain_multiplier: float

_SCENARIOS = [
    WeatherScenario("normal", 0.0, 1.0),
    WeatherScenario("drought", 2.0, 0.3),
    WeatherScenario("flood", -1.0, 2.5),
    WeatherScenario("heat_wave", 5.0, 0.5),
]

class WeatherScenarioSimulator:
    def list_scenarios(self) -> list[WeatherScenario]:
        return list(_SCENARIOS)

    def apply(self, base_temp: float, base_rain: float, scenario: WeatherScenario) -> dict[str, float]:
        return {
            "temperature_c": base_temp + scenario.temp_delta_c,
            "rainfall_mm": base_rain * scenario.rain_multiplier,
        }

__all__ = ["WeatherScenario", "WeatherScenarioSimulator"]
