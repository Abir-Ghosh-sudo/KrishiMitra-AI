"""Crop growth simulation with Mojo acceleration."""

from __future__ import annotations

try:
    import krishimitra_mojo
    from krishimitra_mojo.crop_sim import compute_gdd as _mojo_gdd, simulate_crop_growth
    _MOJO_AVAILABLE = True
except ImportError:
    _MOJO_AVAILABLE = False


def compute_gdd(tmin: float, tmax: float, tbase: float = 10.0) -> float:
    if _MOJO_AVAILABLE:
        try:
            return float(_mojo_gdd(tmin, tmax, tbase))
        except Exception:
            pass
    tavg = (tmin + tmax) / 2.0
    if tavg < tbase:
        return 0.0
    if tavg > 30.0:
        tavg = 30.0
    return tavg - tbase
