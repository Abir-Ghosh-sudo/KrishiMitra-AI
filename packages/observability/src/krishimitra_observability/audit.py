from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger("audit")

@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    resource: str
    outcome: str
    timestamp: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now(tz=timezone.utc))

class AuditLogger:
    def log(self, event: AuditEvent) -> None:
        logger.info(
            "AUDIT actor=%s action=%s resource=%s outcome=%s ts=%s",
            event.actor, event.action, event.resource, event.outcome,
            event.timestamp.isoformat(),
        )

__all__ = ["AuditEvent", "AuditLogger"]
