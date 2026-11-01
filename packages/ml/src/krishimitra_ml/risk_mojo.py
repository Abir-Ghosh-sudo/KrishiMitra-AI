"""Pest and disease risk scoring with Mojo acceleration."""

from __future__ import annotations

try:
    import krishimitra_mojo
    from krishimitra_mojo.risk import compute_pest_risk, compute_disease_risk, batch_risk_scoring
    _MOJO_AVAILABLE = True
except ImportError:
    _MOJO_AVAILABLE = False


def compute_pest_risk_score(temp: float, humidity: float, rainfall: float = 0.0, wind: float = 0.0, leaf_wetness: float = 0.0) -> float:
    if _MOJO_AVAILABLE:
        try:
            return float(compute_pest_risk(temp, humidity, rainfall, wind, leaf_wetness))
        except Exception:
            pass
    risk = 0.0
    if 20.0 <= temp <= 30.0:
        risk += 25.0 * (1.0 - abs(temp - 25.0) / 10.0)
    if humidity > 70.0:
        risk += 20.0 * ((humidity - 70.0) / 30.0)
    if rainfall > 0.0:
        risk += 15.0
    if leaf_wetness > 0.5:
        risk += 25.0 * leaf_wetness
    return max(0.0, min(100.0, risk))


def compute_disease_risk_score(temp: float, humidity: float, leaf_wetness_duration: float = 0.0, rainfall: float = 0.0) -> float:
    if _MOJO_AVAILABLE:
        try:
            return float(compute_disease_risk(temp, humidity, leaf_wetness_duration, rainfall))
        except Exception:
            pass
    risk = 0.0
    if humidity > 80.0:
        risk += 30.0
    if leaf_wetness_duration > 6.0:
        risk += 30.0
    if 15.0 <= temp <= 25.0 and humidity > 80.0:
        risk += 25.0
    return max(0.0, min(100.0, risk))
