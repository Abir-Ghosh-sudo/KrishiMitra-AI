from __future__ import annotations
import hashlib

class CacheKey:
    SEP = ":"
    def __init__(self, *parts: str) -> None:
        self._parts = parts

    def __str__(self) -> str:
        return self.SEP.join(str(p) for p in self._parts)

    def hashed(self, length: int = 12) -> str:
        raw = str(self)
        return hashlib.md5(raw.encode()).hexdigest()[:length]

def build_key(*parts: str) -> str:
    return CacheKey.SEP.join(parts)

__all__ = ["CacheKey", "build_key"]
