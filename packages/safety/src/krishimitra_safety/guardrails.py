from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class SafetyViolation:
    rule: str
    severity: str
    message: str

@dataclass(frozen=True)
class SafetyGuardrail:
    name: str
    severity: str
    check: Callable[[Any], bool]
    message: str

    def evaluate(self, context: Any) -> SafetyViolation | None:
        try:
            if not self.check(context):
                return SafetyViolation(self.name, self.severity, self.message)
        except Exception:
            return SafetyViolation(self.name, "error", f"Guardrail check failed: {self.name}")
        return None

__all__ = ["SafetyGuardrail", "SafetyViolation"]
