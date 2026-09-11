"""Shared application limits for KrishiMitra-AI."""

from __future__ import annotations

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

MAX_TEXT_INPUT_LENGTH = 10_000

__all__ = [
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MAX_TEXT_INPUT_LENGTH",
]