from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class IrrigationEvent:
    event_date: date
    amount_mm: float
    method: str = "drip"
    notes: str = ""

@dataclass
class IrrigationHistory:
    events: list[IrrigationEvent] = field(default_factory=list)

    def add(self, event: IrrigationEvent) -> None:
        self.events.append(event)

    def total_mm(self) -> float:
        return sum(e.amount_mm for e in self.events)

    def recent_total_mm(self, days: int = 7) -> float:
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)
        return sum(e.amount_mm for e in self.events if e.event_date >= cutoff)

__all__ = ["IrrigationEvent", "IrrigationHistory"]
