"""Mojo-accelerated irrigation optimization kernels."""

from __future__ import annotations

import math
import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True, cache=True)
def compute_et0(temperature, humidity, wind_speed, solar_radiation, elevation=0.0):
    """Compute reference evapotranspiration (Penman-Monteith approximation)."""
    T = temperature
    RH = humidity
    U = wind_speed
    Rs = solar_radiation
    # Simplified FAO-56 approximation
    delta = 4098 * (0.6108 * math.exp(17.27 * T / (T + 237.3))) / ((T + 237.3) ** 2)
    gamma = 0.000665 * (101.3 * ((293.0 - 0.0065 * elevation) / 293.0) ** 5.26)
    es = 0.6108 * math.exp(17.27 * T / (T + 237.3))
    ea = es * RH / 100.0
    et0 = (0.408 * delta * Rs + gamma * 900 / (T + 273) * U * (es - ea)) / (delta + gamma * (1 + 0.34 * U))
    return max(0.0, et0)


@jit(nopython=True, fastmath=True, cache=True)
def compute_water_requirement(crop_coefficient, et0, area_hectares, rainfall=0.0, efficiency=0.8):
    """Compute water requirement in cubic meters."""
    etc = crop_coefficient * et0
    net_req = max(0.0, etc - rainfall)
    gross_req = net_req / efficiency
    water_m3 = gross_req * area_hectares * 10.0  # mm * ha = 10 m3
    return water_m3


@jit(nopython=True, fastmath=True, cache=True)
def optimize_water_allocation(demands, available_water, priorities):
    """Optimize water allocation using priority-based allocation."""
    n = len(demands)
    allocation = np.zeros(n, dtype=np.float32)
    remaining = available_water
    # Sort by priority
    for _ in range(n):
        best_idx = -1
        best_prio = -1.0
        for i in range(n):
            if allocation[i] < demands[i] - 1e-6 and priorities[i] > best_prio:
                best_prio = priorities[i]
                best_idx = i
        if best_idx < 0 or remaining < 1e-6:
            break
        alloc = min(demands[best_idx] - allocation[best_idx], remaining)
        allocation[best_idx] += alloc
        remaining -= alloc
    return allocation
