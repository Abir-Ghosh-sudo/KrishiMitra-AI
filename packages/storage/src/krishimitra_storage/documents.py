from __future__ import annotations
import uuid
from .object_store import ObjectStore

class DocumentStore:
    def __init__(self, object_store: ObjectStore) -> None:
        self._store = object_store

    async def save(self, data: bytes, filename: str) -> str:
        key = f"docs/{uuid.uuid4()}_{filename}"
        await self._store.put(key, data, "application/octet-stream")
        return key

    async def load(self, key: str) -> bytes | None:
        return await self._store.get(key)

__all__ = ["DocumentStore"]
