"""Application-level constants for KrishiMitra-AI."""

from __future__ import annotations

APP_NAME = "KrishiMitra-AI"
APP_VERSION = "0.1.0"

DEFAULT_API_PREFIX = "/api"
DEFAULT_API_VERSION = "v1"
DEFAULT_SERVICE_NAME = "krishimitra"

ENV_DEVELOPMENT = "development"
ENV_TESTING = "testing"
ENV_PRODUCTION = "production"

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_API_PREFIX",
    "DEFAULT_API_VERSION",
    "DEFAULT_SERVICE_NAME",
    "ENV_DEVELOPMENT",
    "ENV_TESTING",
    "ENV_PRODUCTION",
]