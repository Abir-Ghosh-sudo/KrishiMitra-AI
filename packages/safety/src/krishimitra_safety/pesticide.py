from __future__ import annotations

_PHI_DAYS: dict[str, int] = {
    "chlorpyrifos": 15, "mancozeb": 7, "imidacloprid": 7,
    "tricyclazole": 21, "emamectin": 3, "spinosad": 1,
}

class PesticideSafetyChecker:
    def check_phi(self, product: str, days_to_harvest: int) -> str | None:
        phi = _PHI_DAYS.get(product.lower(), 0)
        if days_to_harvest < phi:
            return f"{product}: requires {phi}-day PHI ({days_to_harvest} days remaining)."
        return None

    def is_banned(self, product: str) -> bool:
        _BANNED = {"monocrotophos", "endosulfan", "methyl_parathion"}
        return product.lower() in _BANNED

__all__ = ["PesticideSafetyChecker"]
