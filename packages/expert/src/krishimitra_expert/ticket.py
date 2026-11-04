from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

class TicketPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class ExpertTicket:
    farmer_id: str
    issue_type: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    assigned_expert: str | None = None
    resolution: str | None = None

    def assign(self, expert_id: str) -> None:
        self.assigned_expert = expert_id
        self.status = TicketStatus.IN_PROGRESS

    def resolve(self, resolution: str) -> None:
        self.resolution = resolution
        self.status = TicketStatus.RESOLVED

__all__ = ["ExpertTicket", "TicketPriority", "TicketStatus"]
