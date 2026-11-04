from __future__ import annotations
import math
from .coordinates import GeoPoint

_EARTH_RADIUS_KM = 6371.0

def haversine_km(a: GeoPoint, b: GeoPoint) -> float:
    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(h))

__all__ = ["haversine_km"]
