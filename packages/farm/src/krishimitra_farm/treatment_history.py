from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class TreatmentRecord:
    applied_date: date
    product: str
    dose: str
    target: str
    notes: str = ""

@dataclass
class TreatmentHistory:
    records: list[TreatmentRecord] = field(default_factory=list)

    def add(self, record: TreatmentRecord) -> None:
        self.records.append(record)

    def recent(self, days: int = 30) -> list[TreatmentRecord]:
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)
        return [r for r in self.records if r.applied_date >= cutoff]

__all__ = ["TreatmentHistory", "TreatmentRecord"]
