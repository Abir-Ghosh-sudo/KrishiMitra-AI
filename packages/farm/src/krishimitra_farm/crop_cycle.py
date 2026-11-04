from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

class CropCycleStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    HARVESTED = "harvested"
    FAILED = "failed"

@dataclass
class CropCycle:
    crop_name: str
    sowing_date: date
    expected_harvest_date: date
    area_ha: float
    variety: str | None = None
    status: CropCycleStatus = CropCycleStatus.ACTIVE
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actual_yield_kg: float | None = None

    @property
    def is_active(self) -> bool:
        return self.status == CropCycleStatus.ACTIVE

    def harvest(self, yield_kg: float) -> None:
        self.actual_yield_kg = yield_kg
        self.status = CropCycleStatus.HARVESTED

__all__ = ["CropCycle", "CropCycleStatus"]
