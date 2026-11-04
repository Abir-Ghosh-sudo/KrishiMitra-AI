from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class EnergyRecord:
    source: str
    kwh: float

@dataclass
class EnergyUsageTracker:
    _records: list[EnergyRecord] = field(default_factory=list)

    def add(self, record: EnergyRecord) -> None:
        self._records.append(record)

    def total_kwh(self) -> float:
        return sum(r.kwh for r in self._records)

    def renewable_fraction(self) -> float:
        renewable = sum(r.kwh for r in self._records if r.source in ("solar", "wind"))
        total = self.total_kwh()
        return renewable / total if total > 0 else 0.0

__all__ = ["EnergyRecord", "EnergyUsageTracker"]
