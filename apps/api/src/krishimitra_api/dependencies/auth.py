"""Authentication dependencies."""

from __future__ import annotations

from typing import Any


async def get_current_user() -> dict[str, Any]:
    """Get current authenticated user (placeholder)."""
    return {"id": "anonymous", "role": "user"}
