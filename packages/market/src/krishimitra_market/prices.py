from __future__ import annotations
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class CommodityPrice:
    commodity: str
    market: str
    date: date
    min_price_per_quintal: float
    max_price_per_quintal: float
    modal_price_per_quintal: float

class MarketPriceService:
    """Stub — wire up to Agmarknet or eNAM API in production."""
    def __init__(self) -> None:
        self._cache: dict[str, CommodityPrice] = {}

    def store(self, price: CommodityPrice) -> None:
        self._cache[f"{price.commodity}:{price.market}:{price.date}"] = price

    def get_latest(self, commodity: str, market: str) -> CommodityPrice | None:
        matches = [
            v for k, v in self._cache.items()
            if k.startswith(f"{commodity}:{market}:")
        ]
        return max(matches, key=lambda p: p.date) if matches else None

__all__ = ["CommodityPrice", "MarketPriceService"]
