"""Database engine, session factory, and async session management."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DEFAULT_DATABASE_URL = "postgresql+asyncpg://krishimitra:krishimitra@localhost:5432/krishimitra"


def get_default_database_url() -> str:
    """Resolve database connection string from environment or settings."""
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    try:
        from krishimitra_core.config.settings import get_settings

        return get_settings().database_url
    except Exception:
        return DEFAULT_DATABASE_URL


class DatabaseSessionManager:
    """Manages SQLAlchemy async engine and session lifecycle."""

    def __init__(
        self,
        database_url: str | None = None,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_recycle: int = 1800,
        pool_pre_ping: bool = True,
        **engine_kwargs: Any,
    ) -> None:
        self._database_url = database_url or get_default_database_url()
        self._echo = echo
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_recycle = pool_recycle
        self._pool_pre_ping = pool_pre_ping
        self._engine_kwargs = engine_kwargs
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        """Return the active async engine, initializing it if needed."""
        if self._engine is None:
            self.init()
        assert self._engine is not None
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the async session factory, initializing if needed."""
        if self._session_factory is None:
            self.init()
        assert self._session_factory is not None
        return self._session_factory

    def init(self) -> None:
        """Initialize the database engine and session maker."""
        if self._engine is not None:
            return

        self._engine = create_async_engine(
            self._database_url,
            echo=self._echo,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_recycle=self._pool_recycle,
            pool_pre_ping=self._pool_pre_ping,
            **self._engine_kwargs,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        """Dispose of the database engine and connection pool."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a scoped session context with automatic rollback on error."""
        if self._session_factory is None:
            self.init()
        assert self._session_factory is not None

        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Default singleton instance
session_manager = DatabaseSessionManager()


def create_database_engine(
    database_url: str | None = None,
    echo: bool = False,
    pool_size: int = 10,
    max_overflow: int = 20,
    **kwargs: Any,
) -> AsyncEngine:
    """Create a configured async database engine."""
    url = database_url or get_default_database_url()
    return create_async_engine(
        url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
        **kwargs,
    )


def create_session_factory(
    engine: AsyncEngine | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Create an async sessionmaker instance for the provided engine."""
    target_engine = engine or session_manager.engine
    return async_sessionmaker(
        bind=target_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with session_manager.session() as session:
        yield session


# Aliases for compatibility
get_session = get_async_session
AsyncSessionLocal = session_manager.session_factory


__all__ = [
    "DEFAULT_DATABASE_URL",
    "DatabaseSessionManager",
    "create_database_engine",
    "create_session_factory",
    "get_async_session",
    "get_session",
    "get_default_database_url",
    "session_manager",
    "AsyncSessionLocal",
]
