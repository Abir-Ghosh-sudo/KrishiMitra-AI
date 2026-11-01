"""Mojo kernel loader and bridge."""

from __future__ import annotations

import os
import numpy as np

KERNELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kernels")


def get_kernel_path(name: str) -> str:
    """Get path to Mojo kernel file."""
    return os.path.join(KERNELS_DIR, f"{name}.mojo")


def list_kernels() -> list:
    """List available Mojo kernels."""
    if not os.path.exists(KERNELS_DIR):
        return []
    return [f for f in os.listdir(KERNELS_DIR) if f.endswith('.mojo')]
