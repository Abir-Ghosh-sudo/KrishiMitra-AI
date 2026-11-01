"""Mojo-accelerated geospatial computation kernels."""
from __future__ import annotations

import math
import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True, cache=True)
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate Haversine distance between two points in km."""
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@jit(nopython=True, fastmath=True, cache=True)
def compute_raster_stats(values):
    """Compute raster statistics."""
    n = len(values)
    if n == 0:
        return (0.0, 0.0, 0.0, 0.0)
    min_val = values[0]
    max_val = values[0]
    total = 0.0
    for i in range(n):
        v = values[i]
        if v < min_val:
            min_val = v
        if v > max_val:
            max_val = v
        total += v
    mean = total / n
    var = 0.0
    for i in range(n):
        diff = values[i] - mean
        var += diff * diff
    var = var / n
    std = math.sqrt(var)
    return (float(min_val), float(max_val), float(mean), float(std))


def build_spatial_grid(bbox, resolution):
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


def interpolate_grid(points, values, grid):
    """Simple inverse distance weighting."""
    result = []
    for gx, gy in grid:
        num = 0.0
        den = 0.0
        for i in range(len(points)):
            px, py = points[i]
            dx = gx - px
            dy = gy - py
            dist = math.sqrt(dx*dx + dy*dy) + 1e-10
            num += values[i] / dist
            den += 1.0 / dist
        if den > 0:
            result.append(num / den)
        else:
            result.append(0.0)
    return result
