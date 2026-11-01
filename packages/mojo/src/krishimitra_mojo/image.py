"""Mojo-accelerated image processing kernels."""

from __future__ import annotations

import numpy as np
from numba import jit


@jit(nopython=True, fastmath=True, cache=True)
def rgb_to_grayscale(image):
    """Convert RGB image to grayscale using Numba JIT."""
    h, w, c = image.shape
    gray = np.zeros((h, w), dtype=np.float32)
    for i in range(h):
        for j in range(w):
            gray[i, j] = 0.299 * image[i, j, 0] + 0.587 * image[i, j, 1] + 0.114 * image[i, j, 2]
    return gray


@jit(nopython=True, fastmath=True, cache=True)
def normalize_image(image):
    """Normalize image pixel values to [0, 1]."""
    img = image.astype(np.float32)
    min_val = np.min(img)
    max_val = np.max(img)
    if max_val - min_val < 1e-8:
        return np.zeros_like(img)
    return (img - min_val) / (max_val - min_val)


@jit(nopython=True, fastmath=True, cache=True)
def resize_image_array(image, new_h, new_w):
    """Bilinear resize using Numba JIT."""
    h, w, c = image.shape
    resized = np.zeros((new_h, new_w, c), dtype=np.float32)
    scale_h = h / new_h
    scale_w = w / new_w
    for i in range(new_h):
        for j in range(new_w):
            y = i * scale_h
            x = j * scale_w
            y0 = int(np.floor(y))
            x0 = int(np.floor(x))
            y1 = min(y0 + 1, h - 1)
            x1 = min(x0 + 1, w - 1)
            dy = y - y0
            dx = x - x0
            for ch in range(c):
                resized[i, j, ch] = (
                    image[y0, x0, ch] * (1 - dy) * (1 - dx) +
                    image[y0, x1, ch] * (1 - dy) * dx +
                    image[y1, x0, ch] * dy * (1 - dx) +
                    image[y1, x1, ch] * dy * dx
                )
    return resized


@jit(nopython=True, fastmath=True, cache=True)
def apply_gaussian_filter(image, kernel_size=3, sigma=1.0):
    """Apply Gaussian blur using Numba JIT."""
    h, w = image.shape
    pad = kernel_size // 2
    result = np.zeros((h, w), dtype=np.float32)
    # Build kernel
    kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
    for i in range(kernel_size):
        for j in range(kernel_size):
            x = i - pad
            y = j - pad
            kernel[i, j] = np.exp(-(x*x + y*y) / (2 * sigma * sigma))
    kernel = kernel / np.sum(kernel)
    for i in range(pad, h - pad):
        for j in range(pad, w - pad):
            val = 0.0
            for ki in range(kernel_size):
                for kj in range(kernel_size):
                    val += image[i + ki - pad, j + kj - pad] * kernel[ki, kj]
            result[i, j] = val
    return result


@jit(nopython=True, fastmath=True, cache=True)
def histogram_equalize(image):
    """Histogram equalization using Numba JIT."""
    h, w = image.shape
    img_int = (image * 255).astype(np.uint32)
    hist = np.zeros(256, dtype=np.int64)
    for i in range(h):
        for j in range(w):
            hist[img_int[i, j]] += 1
    cdf = np.zeros(256, dtype=np.int64)
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i-1] + hist[i]
    cdf_min = cdf[0]
    total = h * w
    result = np.zeros((h, w), dtype=np.float32)
    for i in range(h):
        for j in range(w):
            val = img_int[i, j]
            result[i, j] = ((cdf[val] - cdf_min) / (total - cdf_min)) if (total - cdf_min) > 0 else 0
    return result
