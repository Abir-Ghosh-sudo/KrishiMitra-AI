"""Mojo-accelerated pest and disease risk scoring kernels."""

from __future__ import annotations

import math
import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True, cache=True)
def compute_pest_risk(temperature, humidity, rainfall, wind_speed, leaf_wetness):
    """Compute pest risk score (0-100)."""
    risk = 0.0
    if 20 <= temperature <= 30:
        risk += 25.0 * (1.0 - abs(temperature - 25.0) / 10.0)
    if humidity > 70:
        risk += 20.0 * ((humidity - 70.0) / 30.0)
    if rainfall > 0:
        risk += 15.0 * min(1.0, rainfall / 10.0)
    if leaf_wetness > 0.5:
        risk += 25.0 * leaf_wetness
    if 1 <= wind_speed <= 5:
        risk += 15.0 * (1.0 - abs(wind_speed - 3.0) / 4.0)
    return min(100.0, max(0.0, risk))


@jit(nopython=True, fastmath=True, cache=True)
def compute_disease_risk(temperature, humidity, leaf_wetness_duration, rainfall, dew_point):
    """Compute disease risk score (0-100)."""
    risk = 0.0
    if humidity > 80:
        risk += 30.0
    elif humidity > 60:
        risk += 15.0
    if leaf_wetness_duration > 6:
        risk += 30.0 * min(1.0, leaf_wetness_duration / 24.0)
    elif leaf_wetness_duration > 2:
        risk += 15.0
    if 15 <= temperature <= 25 and humidity > 80:
        risk += 25.0
    if rainfall > 5:
        risk += 15.0
    return min(100.0, max(0.0, risk))


@jit(nopython=True, fastmath=True, cache=True)
def batch_risk_scoring(temp_array, humid_array, rain_array, wind_array, lw_array):
    """Batch compute pest and disease risk scores."""
    n = len(temp_array)
    pest_risk = np.zeros(n, dtype=np.float32)
    disease_risk = np.zeros(n, dtype=np.float32)
    for i in range(n):
        pest_risk[i] = compute_pest_risk(temp_array[i], humid_array[i], rain_array[i], wind_array[i], lw_array[i])
        disease_risk[i] = compute_disease_risk(temp_array[i], humid_array[i], lw_array[i] * 10.0, rain_array[i], temp_array[i] - 2.0)
    return pest_risk, disease_risk
