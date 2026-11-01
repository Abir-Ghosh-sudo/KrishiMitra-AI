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
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


@jit(nopython=True, fastmath=True, cache=True)
def compute_raster_stats(raster):
    """Compute statistics for raster data."""
    h, w = raster.shape
    total = h * w
    s = 0.0
    s2 = 0.0
    min_val = raster[0, 0]
    max_val = raster[0, 0]
    for i in range(h):
        for j in range(w):
            v = raster[i, j]
            if v < min_val:
                min_val = v
            if v > max_val:
                max_val = v
            s += v
            s2 += v * v
    mean = s / total
    var = (s2 / total) - mean * mean
    std = math.sqrt(max(0.0, var))
    return mean, std, min_val, max_val


@jit(nopython=True, fastmath=True, cache=True)
def build_spatial_grid(xmin, ymin, xmax, ymax, resolution):
    """Build spatial grid coordinates."""
    nx = int((xmax - xmin) / resolution) + 1
    ny = int((ymax - ymin) / resolution) + 1
    grid_x = np.zeros((ny, nx), dtype=np.float32)
    grid_y = np.zeros((ny, nx), dtype=np.float32)
    for i in range(ny):
        for j in range(nx):
            grid_x[i, j] = xmin + j * resolution
            grid_y[i, j] = ymin + i * resolution
    return grid_x, grid_y, nx, ny


@jit(nopython=True, fastmath=True, cache=True)
def interpolate_grid(x_points, y_points, values, grid_x, grid_y):
    """Inverse distance weighting interpolation."""
    ny, nx = grid_x.shape
    n = len(values)
    result = np.zeros((ny, nx), dtype=np.float32)
    power = 2.0
    for i in range(ny):
        for j in range(nx):
            gx, gy = grid_x[i, j], grid_y[i, j]
            sum_w = 0.0
            sum_wv = 0.0
            for k in range(n):
                dx = gx - x_points[k]
                dy = gy - y_points[k]
                d2 = dx*dx + dy*dy
                if d2 < 1e-12:
                    sum_wv = values[k]
                    sum_w = 1.0
                    break
                w = 1.0 / (d2 ** (power/2.0))
                sum_w += w
                sum_wv += w * values[k]
            if sum_w > 0:
                result[i, j] = sum_wv / sum_w
            else:
                result[i, j] = 0.0
    return result
