from __future__ import annotations
from .scenario import Scenario

class ScenarioComparator:
    def compare(self, scenarios: list[Scenario], metric: str) -> Scenario | None:
        valid = [s for s in scenarios if metric in s.results]
        if not valid:
            return None
        return max(valid, key=lambda s: s.results[metric])

__all__ = ["ScenarioComparator"]
