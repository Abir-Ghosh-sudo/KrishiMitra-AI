from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ResourceAllocation:
    resource: str
    allocated: float
    unit: str
    priority: int

class ResourceAllocator:
    def allocate(
        self,
        resources: dict[str, float],
        demands: dict[str, float],
    ) -> list[ResourceAllocation]:
        result: list[ResourceAllocation] = []
        for i, (name, demand) in enumerate(demands.items()):
            available = resources.get(name, 0.0)
            result.append(ResourceAllocation(
                resource=name,
                allocated=min(demand, available),
                unit="unit",
                priority=i,
            ))
        return result

__all__ = ["ResourceAllocation", "ResourceAllocator"]
