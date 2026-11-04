from __future__ import annotations
from .coordinates import GeoPoint

def reverse_geocode_stub(point: GeoPoint) -> str:
    return f"Location at {point.latitude:.4f},{point.longitude:.4f}"

__all__ = ["reverse_geocode_stub"]
