from __future__ import annotations

_CONTRAINDICATIONS: dict[str, list[str]] = {
    "mancozeb": ["copper_oxychloride"],
    "imidacloprid": ["dimethoate"],
}

class ContraindicationChecker:
    def check(self, product: str, other_products: list[str]) -> list[str]:
        contraindicated = _CONTRAINDICATIONS.get(product.lower(), [])
        return [p for p in other_products if p.lower() in contraindicated]

__all__ = ["ContraindicationChecker"]
