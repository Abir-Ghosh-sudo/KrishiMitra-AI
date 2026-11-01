"""Mojo-accelerated crop growth simulation kernels."""

from __future__ import annotations

import math
import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True, cache=True)
def compute_gdd(t_min, t_max, t_base):
    """Compute Growing Degree Days."""
    t_avg = (t_min + t_max) / 2.0
    if t_avg < t_base:
        return 0.0
    if t_avg > 30.0:
        t_avg = 30.0
    return t_avg - t_base


@jit(nopython=True, fastmath=True, cache=True)
def compute_biomass(gdd_accumulated, radiation, lai, conversion_efficiency=0.02):
    """Compute accumulated biomass."""
    intercepted = radiation * (1.0 - math.exp(-0.5 * lai))
    return intercepted * conversion_efficiency * gdd_accumulated / 100.0


@jit(nopython=True, fastmath=True, cache=True)
def simulate_crop_growth(days, temp_min, temp_max, rainfall, soil_moisture, t_base, crop_type=0):
    """Simulate crop growth over days."""
    growth = np.zeros(days, dtype=np.float32)
    biomass = np.zeros(days, dtype=np.float32)
    lai = np.zeros(days, dtype=np.float32)
    gdd_accum = 0.0
    bio_accum = 0.0
    lai_current = 0.01
    
    for d in range(days):
        gdd = compute_gdd(temp_min[d], temp_max[d], t_base)
        gdd_accum += gdd
        
        # LAI growth
        if gdd_accum < 500:
            lai_current = min(6.0, lai_current * (1.0 + 0.02 * (1.0 if soil_moisture[d] > 0.3 else 0.5)))
        elif gdd_accum < 1500:
            lai_current = max(0.1, lai_current * 0.995)
        else:
            lai_current = max(0.01, lai_current * 0.99)
        lai[d] = lai_current
        
        # Biomass
        rad = max(0.0, 15.0 - abs(temp_max[d] - 25.0))
        bio_accum += compute_biomass(gdd, rad, lai_current)
        biomass[d] = bio_accum
        growth[d] = min(1.0, gdd_accum / 2500.0)
    
    return growth, biomass, lai
