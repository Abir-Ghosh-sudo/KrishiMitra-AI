from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

@dataclass
class DiseaseRecord:
    disease_name: str
    detected_on: date
    crop: str
    severity: str
    treatment_applied: str | None = None
    outcome: str | None = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class DiseaseHistory:
    records: list[DiseaseRecord] = field(default_factory=list)

    def add(self, record: DiseaseRecord) -> None:
        self.records.append(record)

    def recent(self, days: int = 30) -> list[DiseaseRecord]:
        cutoff = date.today()
        from datetime import timedelta
        cutoff -= timedelta(days=days)
        return [r for r in self.records if r.detected_on >= cutoff]

__all__ = ["DiseaseHistory", "DiseaseRecord"]
