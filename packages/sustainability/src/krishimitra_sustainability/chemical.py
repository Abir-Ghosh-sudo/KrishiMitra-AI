from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ChemicalApplication:
    product: str
    dose_kg_ha: float
    category: str

@dataclass
class ChemicalUsageTracker:
    _applications: list[ChemicalApplication] = field(default_factory=list)

    def add(self, app: ChemicalApplication) -> None:
        self._applications.append(app)

    def total_pesticide_kg_ha(self) -> float:
        return sum(a.dose_kg_ha for a in self._applications if a.category == "pesticide")

    def application_count(self) -> int:
        return len(self._applications)

__all__ = ["ChemicalApplication", "ChemicalUsageTracker"]
