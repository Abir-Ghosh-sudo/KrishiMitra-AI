"""Mojo-accelerated soil analysis kernels."""
from __future__ import annotations

import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True, cache=True)
def compute_water_holding_capacity(sand, silt, clay, organic_matter):
    total = sand + silt + clay
    if total < 1e-8:
        return 0.0
    s = sand / total
    c = clay / total
    om = organic_matter / 100.0
    whc = 0.05 + 0.3 * c + 0.1 * om + 0.05 * (1.0 - s)
    return whc * 100.0


@jit(nopython=True, fastmath=True, cache=True)
def compute_soil_features(ph, oc, n, p, k):
    score = 0.0
    if ph >= 6.0 and ph <= 7.5:
        score += 20.0
    else:
        score += 10.0
    if oc > 0.75:
        score += 20.0
    if n > 280:
        score += 20.0
    if p > 25:
        score += 20.0
    if k > 280:
        score += 20.0
    return score


def extract_soil_features(ph, oc, n, p, k):
    return compute_soil_features(ph, oc, n, p, k)


@jit(nopython=True, fastmath=True, cache=True)
def compute_soil_texture(sand, silt, clay):
    total = sand + silt + clay
    if total < 1e-8:
        return (0.0, 0.0, 0.0, "unknown")
    s = sand / total * 100.0
    si = silt / total * 100.0
    c = clay / total * 100.0
    if c > 40:
        name = "clay"
    elif c > 27 and si < 28:
        name = "clay_loam"
    elif si > 80:
        name = "silt"
    elif si > 50:
        name = "silt_loam"
    elif c > 20 and si > 40:
        name = "loam"
    elif c > 7 and si < 50:
        name = "sandy_loam"
    else:
        name = "sandy"
    return (float(s), float(si), float(c), name)
