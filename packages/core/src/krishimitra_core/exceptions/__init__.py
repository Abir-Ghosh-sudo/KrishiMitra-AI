"""Shared exception hierarchy for KrishiMitra-AI."""

from __future__ import annotations

from .base import (
    ConfigurationError,
    KrishiMitraError,
    ResourceNotFoundError,
    ServiceError,
    ValidationError,
)

__all__ = [
    "ConfigurationError",
    "KrishiMitraError",
    "ResourceNotFoundError",
    "ServiceError",
    "ValidationError",
]