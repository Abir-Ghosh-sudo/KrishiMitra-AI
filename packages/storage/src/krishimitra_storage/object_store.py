from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

class StorageError(Exception):
    pass

class ObjectStore:
    """Stub — replace with S3/GCS/MinIO client in production."""
    def __init__(self, bucket: str = "krishimitra") -> None:
        self._bucket = bucket
        self._store: dict[str, bytes] = {}

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self._store[key] = data
        logger.debug("ObjectStore.put key=%s size=%d", key, len(data))
        return f"local://{self._bucket}/{key}"

    async def get(self, key: str) -> bytes | None:
        return self._store.get(key)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

__all__ = ["ObjectStore", "StorageError"]
