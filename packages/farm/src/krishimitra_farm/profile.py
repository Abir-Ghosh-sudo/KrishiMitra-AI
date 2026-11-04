from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class FarmProfile:
    farmer_id: str
    name: str
    phone: str
    location_name: str
    latitude: float = 0.0
    longitude: float = 0.0
    total_area_ha: float = 0.0
    crops: list[str] = field(default_factory=list)
    language: str = "hi"
    soil_type: str | None = None

__all__ = ["FarmProfile"]
