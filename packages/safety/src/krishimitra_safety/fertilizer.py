from __future__ import annotations

_MAX_UREA_KG_PER_ACRE = 100.0

class FertilizerSafetyChecker:
    def check_urea_overdose(self, kg_per_acre: float) -> str | None:
        if kg_per_acre > _MAX_UREA_KG_PER_ACRE:
            return f"Urea dose {kg_per_acre}kg/acre exceeds safe limit of {_MAX_UREA_KG_PER_ACRE}kg/acre."
        return None

    def check_pre_harvest_interval(self, product: str, days_to_harvest: int) -> str | None:
        phi = {"urea": 0, "dap": 0, "mancozeb": 7, "chlorpyrifos": 15}
        required = phi.get(product.lower(), 0)
        if days_to_harvest < required:
            return f"{product}: {required}-day pre-harvest interval not met ({days_to_harvest} days remaining)."
        return None

__all__ = ["FertilizerSafetyChecker"]
