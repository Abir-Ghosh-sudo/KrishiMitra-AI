from __future__ import annotations
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")

    def __str__(self) -> str:
        return f"{self.latitude:.5f},{self.longitude:.5f}"

@dataclass(frozen=True)
class BoundingBox:
    north: float
    south: float
    east: float
    west: float

    def contains(self, point: GeoPoint) -> bool:
        return self.south <= point.latitude <= self.north and self.west <= point.longitude <= self.east

__all__ = ["BoundingBox", "GeoPoint"]
