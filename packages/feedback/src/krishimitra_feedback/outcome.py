from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class OutcomeRecord:
    recommendation_id: str
    followed: bool
    outcome_description: str
    measured_on: date
    yield_improvement_pct: float | None = None

@dataclass
class OutcomeTracker:
    _records: list[OutcomeRecord] = field(default_factory=list)

    def record(self, outcome: OutcomeRecord) -> None:
        self._records.append(outcome)

    def follow_through_rate(self) -> float:
        if not self._records:
            return 0.0
        return sum(1 for r in self._records if r.followed) / len(self._records)

__all__ = ["OutcomeRecord", "OutcomeTracker"]
