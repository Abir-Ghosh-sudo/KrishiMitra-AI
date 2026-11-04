from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class AlertPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass(frozen=True)
class AlertRule:
    name: str
    priority: AlertPriority
    condition: Callable[[dict[str, Any]], bool]
    message_template: str

@dataclass
class AlertEngine:
    rules: list[AlertRule] = field(default_factory=list)

    def add_rule(self, rule: AlertRule) -> None:
        self.rules.append(rule)

    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        triggered: list[dict[str, Any]] = []
        for rule in self.rules:
            try:
                if rule.condition(context):
                    triggered.append({
                        "rule": rule.name,
                        "priority": rule.priority,
                        "message": rule.message_template,
                    })
            except Exception as exc:
                logger.warning("Alert rule %s failed: %s", rule.name, exc)
        return triggered

__all__ = ["AlertEngine", "AlertPriority", "AlertRule"]
