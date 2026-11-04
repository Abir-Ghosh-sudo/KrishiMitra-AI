from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(frozen=True)
class ConsentRecord:
    farmer_id: str
    purpose: str
    granted: bool
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

class ConsentStore:
    def __init__(self) -> None:
        self._records: list[ConsentRecord] = []

    def record(self, rec: ConsentRecord) -> None:
        self._records.append(rec)

    def has_consent(self, farmer_id: str, purpose: str) -> bool:
        for r in reversed(self._records):
            if r.farmer_id == farmer_id and r.purpose == purpose:
                return r.granted
        return False

__all__ = ["ConsentRecord", "ConsentStore"]
