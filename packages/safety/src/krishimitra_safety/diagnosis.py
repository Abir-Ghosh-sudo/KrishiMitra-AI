from __future__ import annotations

_DANGEROUS_COMBOS: set[frozenset[str]] = {
    frozenset({"mancozeb", "copper_oxychloride"}),
}

class DiagnosisSafetyChecker:
    def check_chemical_combo(self, chemicals: list[str]) -> list[str]:
        warnings: list[str] = []
        combo = frozenset(c.lower() for c in chemicals)
        for banned in _DANGEROUS_COMBOS:
            if banned.issubset(combo):
                warnings.append(f"Dangerous combination: {', '.join(banned)}")
        return warnings

__all__ = ["DiagnosisSafetyChecker"]
