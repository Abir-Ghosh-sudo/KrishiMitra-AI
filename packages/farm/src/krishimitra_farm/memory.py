from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class MemoryEntry:
    key: str
    value: object
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

@dataclass
class FarmMemory:
    """Short-term contextual memory for a farm session."""
    _entries: dict[str, MemoryEntry] = field(default_factory=dict)

    def remember(self, key: str, value: object) -> None:
        self._entries[key] = MemoryEntry(key=key, value=value)

    def recall(self, key: str) -> object | None:
        entry = self._entries.get(key)
        return entry.value if entry else None

    def forget(self, key: str) -> None:
        self._entries.pop(key, None)

    def clear(self) -> None:
        self._entries.clear()

__all__ = ["FarmMemory", "MemoryEntry"]
