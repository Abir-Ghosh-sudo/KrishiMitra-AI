"""Mojo-accelerated numerical kernels for KrishiMitra-AI.

Provides JIT-compiled kernels using Numba for fast image processing,
geospatial computations, soil analysis, irrigation optimization,
crop growth simulation, and pest/disease risk scoring.
"""

from __future__ import annotations

__version__ = "0.1.0"

from .image import (
    resize_image_array,
    normalize_image,
    apply_gaussian_filter,
    histogram_equalize,
    rgb_to_grayscale,
)
from .geospatial import (
    haversine_distance,
    compute_raster_stats,
    build_spatial_grid,
    interpolate_grid,
)
from .soil import (
    compute_soil_texture,
    extract_soil_features,
    compute_water_holding_capacity,
)
from .irrigation import (
    compute_water_requirement,
    optimize_water_allocation,
    compute_et0,
)
from .crop_sim import (
    simulate_crop_growth,
    compute_gdd,
    compute_biomass,
)
from .risk import (
    compute_pest_risk,
    compute_disease_risk,
    batch_risk_scoring,
)

__all__ = [
    "resize_image_array",
    "normalize_image",
    "apply_gaussian_filter",
    "histogram_equalize",
    "rgb_to_grayscale",
    "haversine_distance",
    "compute_raster_stats",
    "build_spatial_grid",
    "interpolate_grid",
    "compute_soil_texture",
    "extract_soil_features",
    "compute_water_holding_capacity",
    "compute_water_requirement",
    "optimize_water_allocation",
    "compute_et0",
    "simulate_crop_growth",
    "compute_gdd",
    "compute_biomass",
    "compute_pest_risk",
    "compute_disease_risk",
    "batch_risk_scoring",
]
