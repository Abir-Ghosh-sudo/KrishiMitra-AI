"""Unit of work pattern for database transactions."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .session import session_manager


class UnitOfWork:
    """Unit of work for managing database transactions."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session
        self._managed = session is None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session not initialized")
        return self._session

    async def __aenter__(self) -> "UnitOfWork":
        if self._managed:
            self._session_cm = session_manager.session()
            self._session = await self._session_cm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None and self._session is not None:
            await self._session.rollback()
        elif self._session is not None:
            await self._session.commit()
        if self._managed and hasattr(self, "_session_cm"):
            await self._session_cm.__aexit__(exc_type, exc_val, exc_tb)


@asynccontextmanager
async def unit_of_work() -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork() as uow:
        yield uow
