"""Database layer for KrishiMitra-AI."""

from __future__ import annotations

from .session import (
    DatabaseSessionManager,
    async_sessionmaker,
    create_database_engine,
    create_session_factory,
    get_async_session,
    get_default_database_url,
    get_session,
    session_manager,
)

__all__ = [
    "DatabaseSessionManager",
    "async_sessionmaker",
    "create_database_engine",
    "create_session_factory",
    "get_async_session",
    "get_default_database_url",
    "get_session",
    "session_manager",
]

__version__ = "0.1.0"
