"""Base exception hierarchy for KrishiMitra-AI."""

from __future__ import annotations

from typing import Any


class KrishiMitraError(Exception):
    """Base exception for all expected KrishiMitra-AI application errors."""

    error_code = "KRISHIMITRA_ERROR"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        return self.message


class ConfigurationError(KrishiMitraError):
    """Raised when application configuration is invalid."""

    error_code = "CONFIGURATION_ERROR"


class ValidationError(KrishiMitraError):
    """Raised when application or domain input fails validation."""

    error_code = "VALIDATION_ERROR"


class ResourceNotFoundError(KrishiMitraError):
    """Raised when a requested resource cannot be found."""

    error_code = "RESOURCE_NOT_FOUND"


class ServiceError(KrishiMitraError):
    """Raised when an internal or external service operation fails."""

    error_code = "SERVICE_ERROR"


__all__ = [
    "ConfigurationError",
    "KrishiMitraError",
    "ResourceNotFoundError",
    "ServiceError",
    "ValidationError",
]