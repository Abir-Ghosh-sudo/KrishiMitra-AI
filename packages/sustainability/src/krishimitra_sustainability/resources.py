from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ResourceUsage:
    resource: str
    used: float
    unit: str
    budget: float

@dataclass
class ResourceTracker:
    _usages: list[ResourceUsage] = field(default_factory=list)

    def add(self, usage: ResourceUsage) -> None:
        self._usages.append(usage)

    def over_budget(self) -> list[ResourceUsage]:
        return [u for u in self._usages if u.used > u.budget]

    def efficiency_pct(self, resource: str) -> float:
        recs = [u for u in self._usages if u.resource == resource]
        if not recs:
            return 0.0
        return sum(u.budget / max(u.used, 0.001) for u in recs) / len(recs) * 100

__all__ = ["ResourceTracker", "ResourceUsage"]
