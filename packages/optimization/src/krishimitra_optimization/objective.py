from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Sequence

@dataclass(frozen=True)
class OptimizationResult:
    optimal_value: float
    inputs: dict[str, float]
    converged: bool
    iterations: int

@dataclass(frozen=True)
class ObjectiveFunction:
    name: str
    fn: Callable[..., float]
    minimize: bool = True

    def evaluate(self, **kwargs: float) -> float:
        return self.fn(**kwargs)

__all__ = ["ObjectiveFunction", "OptimizationResult"]
