from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta

@dataclass(frozen=True)
class RetentionPolicy:
    data_category: str
    retention_days: int

    @property
    def duration(self) -> timedelta:
        return timedelta(days=self.retention_days)

DEFAULT_POLICIES: list[RetentionPolicy] = [
    RetentionPolicy("conversation", 90),
    RetentionPolicy("farm_profile", 1825),
    RetentionPolicy("audit_log", 365),
    RetentionPolicy("feedback", 180),
]

__all__ = ["DEFAULT_POLICIES", "RetentionPolicy"]
