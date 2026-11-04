from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class YieldRecord:
    season: str
    crop: str
    area_ha: float
    yield_kg: float

    @property
    def yield_per_ha(self) -> float:
        return self.yield_kg / self.area_ha if self.area_ha > 0 else 0.0

@dataclass
class YieldHistory:
    records: list[YieldRecord] = field(default_factory=list)

    def add(self, record: YieldRecord) -> None:
        self.records.append(record)

    def average_yield_per_ha(self, crop: str | None = None) -> float:
        recs = [r for r in self.records if crop is None or r.crop.lower() == crop.lower()]
        if not recs:
            return 0.0
        return sum(r.yield_per_ha for r in recs) / len(recs)

__all__ = ["YieldHistory", "YieldRecord"]
