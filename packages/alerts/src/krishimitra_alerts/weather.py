from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class WeatherAlert:
    alert_type: str
    severity: str
    description: str
    action: str

class WeatherAlertGenerator:
    def generate_flood(self, rain_mm: float) -> WeatherAlert:
        return WeatherAlert(
            alert_type="flood",
            severity="critical" if rain_mm > 64 else "high",
            description=f"Heavy rain expected: {rain_mm:.0f} mm.",
            action="Protect crops and clear drainage channels.",
        )

    def generate_heat(self, temp_c: float) -> WeatherAlert:
        return WeatherAlert(
            alert_type="heat_stress",
            severity="high" if temp_c > 42 else "moderate",
            description=f"Extreme temperature: {temp_c:.1f}°C.",
            action="Irrigate during early morning; provide shade for livestock.",
        )

__all__ = ["WeatherAlert", "WeatherAlertGenerator"]
