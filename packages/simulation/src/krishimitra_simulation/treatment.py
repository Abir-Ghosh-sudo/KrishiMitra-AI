from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TreatmentSimResult:
    product: str
    disease_control_pct: float
    cost_per_acre: float

class TreatmentSimulator:
    _EFFICACY: dict[str, float] = {
        "mancozeb": 0.75, "chlorothalonil": 0.80,
        "tricyclazole": 0.85, "propiconazole": 0.88,
    }

    def simulate(self, product: str, dose_g_l: float, cost_per_acre: float) -> TreatmentSimResult:
        efficacy = self._EFFICACY.get(product.lower(), 0.60) * min(1.0, dose_g_l / 2.0)
        return TreatmentSimResult(product, round(efficacy * 100, 1), cost_per_acre)

__all__ = ["TreatmentSimResult", "TreatmentSimulator"]
