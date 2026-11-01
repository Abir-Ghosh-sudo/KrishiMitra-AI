"""Soil analysis with Mojo acceleration."""

from __future__ import annotations

try:
    import krishimitra_mojo
    from krishimitra_mojo.soil import compute_water_holding_capacity as _mojo_whc, compute_soil_features
    _MOJO_AVAILABLE = True
except ImportError:
    _MOJO_AVAILABLE = False


def compute_water_holding_capacity(sand: float, silt: float, clay: float, organic_matter: float = 0.0) -> float:
    """Compute water holding capacity."""
    if _MOJO_AVAILABLE:
        try:
            return float(_mojo_whc(sand, silt, clay, organic_matter))
        except Exception:
            pass
    total = sand + silt + clay
    if total < 1e-8:
        return 0.0
    s, c = sand / total, clay / total
    om = organic_matter / 100.0
    whc = 0.05 + 0.3 * c + 0.1 * om + 0.05 * (1.0 - s)
    return whc * 100.0


def extract_soil_features(ph: float, organic_carbon: float, nitrogen: float, phosphorus: float, potassium: float) -> float:
    """Extract soil quality features."""
    if _MOJO_AVAILABLE:
        try:
            return float(compute_soil_features(ph, organic_carbon, nitrogen, phosphorus, potassium))
        except Exception:
            pass
    score = 0.0
    if 6.0 <= ph <= 7.5:
        score += 20.0
    else:
        score += 10.0
    if organic_carbon > 0.75:
        score += 20.0
    if nitrogen > 280:
        score += 20.0
    if phosphorus > 25:
        score += 20.0
    if potassium > 280:
        score += 20.0
    return score
