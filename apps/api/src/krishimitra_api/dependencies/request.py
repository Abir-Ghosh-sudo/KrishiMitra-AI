"""Request dependencies."""

from __future__ import annotations

from fastapi import Request


def get_request_id(request: Request) -> str | None:
    """Extract request ID from request state."""
    return getattr(request.state, "request_id", None)
