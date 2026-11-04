from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

class GrowthStage(StrEnum):
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    GRAIN_FILL = "grain_fill"
    MATURITY = "maturity"
    HARVEST = "harvest"

_STAGE_THRESHOLDS: dict[str, list[tuple[int, GrowthStage]]] = {
    "rice": [
        (7, GrowthStage.GERMINATION), (25, GrowthStage.SEEDLING),
        (55, GrowthStage.VEGETATIVE), (80, GrowthStage.FLOWERING),
        (100, GrowthStage.GRAIN_FILL), (120, GrowthStage.MATURITY),
    ],
    "wheat": [
        (10, GrowthStage.GERMINATION), (30, GrowthStage.SEEDLING),
        (60, GrowthStage.VEGETATIVE), (85, GrowthStage.FLOWERING),
        (105, GrowthStage.GRAIN_FILL), (120, GrowthStage.MATURITY),
    ],
    "default": [
        (10, GrowthStage.GERMINATION), (30, GrowthStage.SEEDLING),
        (60, GrowthStage.VEGETATIVE), (80, GrowthStage.FLOWERING),
        (100, GrowthStage.GRAIN_FILL), (120, GrowthStage.MATURITY),
    ],
}

def estimate_stage(crop: str, sowing_date: date, today: date | None = None) -> GrowthStage:
    today = today or date.today()
    days = (today - sowing_date).days
    thresholds = _STAGE_THRESHOLDS.get(crop.lower(), _STAGE_THRESHOLDS["default"])
    for threshold, stage in thresholds:
        if days <= threshold:
            return stage
    return GrowthStage.HARVEST

__all__ = ["GrowthStage", "estimate_stage"]
