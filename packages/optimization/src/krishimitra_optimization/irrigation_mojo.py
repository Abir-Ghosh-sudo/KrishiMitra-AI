"""Irrigation optimization with Mojo acceleration."""

from __future__ import annotations

try:
    import krishimitra_mojo
    from krishimitra_mojo.irrigation import compute_et0 as _mojo_et0, compute_water_requirement as _mojo_wr
    _MOJO_AVAILABLE = True
except ImportError:
    _MOJO_AVAILABLE = False


def compute_et0(temp: float, humidity: float, wind: float, radiation: float) -> float:
    if _MOJO_AVAILABLE:
        try:
            return float(_mojo_et0(temp, humidity, wind, radiation))
        except Exception:
            pass
    import math
    delta = 4098.0 * (0.6108 * math.exp(17.27 * temp / (temp + 237.3))) / ((temp + 237.3) ** 2)
    gamma = 0.665
    es = 0.6108 * math.exp(17.27 * temp / (temp + 237.3))
    ea = es * humidity / 100.0
    et0 = (0.408 * delta * radiation + gamma * 900.0 / (temp + 273.0) * wind * (es - ea)) / (delta + gamma * (1.0 + 0.34 * wind))
    return max(0.0, et0)


def compute_water_requirement(kc: float, et0: float, area_ha: float, rainfall: float = 0.0) -> float:
    if _MOJO_AVAILABLE:
        try:
            return float(_mojo_wr(kc, et0, area_ha, rainfall))
        except Exception:
            pass
    etc = kc * et0
    net_req = etc - rainfall
    if net_req < 0.0:
        return 0.0
    return net_req / 0.8 * area_ha * 10.0
