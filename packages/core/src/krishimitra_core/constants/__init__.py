"""Shared constants for KrishiMitra-AI."""

from __future__ import annotations

from .application import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_API_PREFIX,
    DEFAULT_API_VERSION,
    DEFAULT_SERVICE_NAME,
    ENV_DEVELOPMENT,
    ENV_PRODUCTION,
    ENV_TESTING,
)
from .limits import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MAX_TEXT_INPUT_LENGTH,
)

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_API_PREFIX",
    "DEFAULT_API_VERSION",
    "DEFAULT_SERVICE_NAME",
    "DEFAULT_PAGE_SIZE",
    "ENV_DEVELOPMENT",
    "ENV_PRODUCTION",
    "ENV_TESTING",
    "MAX_PAGE_SIZE",
    "MAX_TEXT_INPUT_LENGTH",
]