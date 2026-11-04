from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IrrigationAlert:
    field_id: str
    water_deficit_mm: float
    recommended_mm: float
    urgency: str

class IrrigationAlertGenerator:
    def generate(self, field_id: str, deficit_mm: float) -> IrrigationAlert:
        if deficit_mm > 30:
            urgency = "high"
        elif deficit_mm > 15:
            urgency = "medium"
        else:
            urgency = "low"
        return IrrigationAlert(
            field_id=field_id,
            water_deficit_mm=deficit_mm,
            recommended_mm=deficit_mm * 1.1,
            urgency=urgency,
        )

__all__ = ["IrrigationAlert", "IrrigationAlertGenerator"]
