"""Mojo-accelerated soil analysis kernels."""

from __future__ import annotations

import math
import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True, cache=True)
def compute_soil_texture(sand, silt, clay):
    """Compute USDA soil texture class."""
    total = sand + silt + clay
    if total < 1e-8:
        return 0
    s = sand / total * 100
    si = silt / total * 100
    c = clay / total * 100
    if c >= 40:
        return 1  # clay
    elif c >= 27 and si >= 40:
        return 2  # silty clay loam
    elif c >= 27 and si < 40:
        return 3  # clay loam
    elif si >= 80:
        return 4  # silt
    elif si >= 50:
        return 5  # silt loam
    elif s >= 70:
        return 6  # sand
    elif s >= 50:
        return 7  # sandy loam
    else:
        return 8  # loam


@jit(nopython=True, fastmath=True, cache=True)
def extract_soil_features(ph, organic_carbon, nitrogen, phosphorus, potassium, sand, silt, clay):
    """Extract soil features as array."""
    features = np.zeros(10, dtype=np.float32)
    features[0] = ph
    features[1] = organic_carbon
    features[2] = nitrogen
    features[3] = phosphorus
    features[4] = potassium
    features[5] = sand
    features[6] = silt
    features[7] = clay
    total = sand + silt + clay
    if total > 1e-8:
        features[8] = sand / total
        features[9] = clay / total
    return features


@jit(nopython=True, fastmath=True, cache=True)
def compute_water_holding_capacity(sand, silt, clay, organic_matter):
    """Compute field capacity water holding capacity."""
    total = sand + silt + clay
    if total < 1e-8:
        return 0.0
    s = sand / total
    c = clay / total
    om = organic_matter / 100.0
    whc = 0.05 + 0.3 * c + 0.1 * om + 0.05 * (1 - s)
    return whc * 100.0
