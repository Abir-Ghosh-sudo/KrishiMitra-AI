"""Geospatial utilities with Mojo acceleration."""

from __future__ import annotations

import math
from typing import List, Tuple

try:
    import krishimitra_mojo
    from krishimitra_mojo.geospatial import haversine_distance as _mojo_haversine
    _MOJO_AVAILABLE = True
except ImportError:
    _MOJO_AVAILABLE = False


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula."""
    if _MOJO_AVAILABLE:
        try:
            return float(_mojo_haversine(lat1, lon1, lat2, lon2))
        except Exception:
            pass
    R = 6371.0
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def compute_raster_stats(values: list) -> dict:
    """Compute raster statistics."""
    if not values:
        return {"min": 0, "max": 0, "mean": 0, "std": 0}
    if _MOJO_AVAILABLE:
        try:
            return krishimitra_mojo.compute_raster_stats(values)
        except Exception:
            pass
    total = sum(values)
    mean = total / len(values)
    var = sum((x - mean) ** 2 for x in values) / len(values)
    std = math.sqrt(var)
    return {"min": min(values), "max": max(values), "mean": mean, "std": std}


def build_spatial_grid(bbox: Tuple[float, float, float, float], resolution: float) -> List[Tuple[float, float]]:
    """Build spatial grid over bounding box."""
    if _MOJO_AVAILABLE:
        try:
            return krishimitra_mojo.build_spatial_grid(bbox, resolution)
        except Exception:
            pass
    minx, miny, maxx, maxy = bbox
    grid = []
    x = minx
    while x <= maxx:
        y = miny
        while y <= maxy:
            grid.append((x, y))
            y += resolution
        x += resolution
    return grid
