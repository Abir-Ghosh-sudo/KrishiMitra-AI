"""API error handling."""

from __future__ import annotations

from .handlers import register_exception_handlers
from .responses import APIErrorDetail, APIErrorResponse, error_response

__all__ = [
    "register_exception_handlers",
    "APIErrorDetail",
    "APIErrorResponse",
    "error_response",
]
