from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Scenario:
    name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)

class ScenarioRunner:
    def run(self, scenario: Scenario, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> Scenario:
        scenario.results = fn(scenario.parameters)
        return scenario

__all__ = ["Scenario", "ScenarioRunner"]
