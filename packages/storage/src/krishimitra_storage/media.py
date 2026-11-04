from __future__ import annotations
import uuid
from .object_store import ObjectStore

class MediaStore:
    def __init__(self, object_store: ObjectStore) -> None:
        self._store = object_store

    async def save(self, data: bytes, content_type: str = "image/jpeg") -> str:
        ext = content_type.split("/")[-1]
        key = f"media/{uuid.uuid4()}.{ext}"
        await self._store.put(key, data, content_type)
        return key

    async def load(self, key: str) -> bytes | None:
        return await self._store.get(key)

__all__ = ["MediaStore"]
