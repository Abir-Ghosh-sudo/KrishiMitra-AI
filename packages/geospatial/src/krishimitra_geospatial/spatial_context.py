from __future__ import annotations
from dataclasses import dataclass
from .coordinates import GeoPoint

@dataclass
class SpatialContext:
    point: GeoPoint
    state: str | None = None
    district: str | None = None
    village: str | None = None
    agro_zone: str | None = None

__all__ = ["SpatialContext"]
