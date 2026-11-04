from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Constraint:
    name: str
    check: Callable[..., bool]
    description: str = ""

    def is_satisfied(self, **kwargs: float) -> bool:
        return self.check(**kwargs)

@dataclass
class ConstraintSet:
    constraints: list[Constraint]

    def all_satisfied(self, **kwargs: float) -> bool:
        return all(c.is_satisfied(**kwargs) for c in self.constraints)

    def violations(self, **kwargs: float) -> list[str]:
        return [c.name for c in self.constraints if not c.is_satisfied(**kwargs)]

__all__ = ["Constraint", "ConstraintSet"]
