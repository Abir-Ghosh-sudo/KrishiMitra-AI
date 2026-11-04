from __future__ import annotations
import logging
from .ticket import ExpertTicket, TicketPriority
from .routing import ExpertRouter

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self, router: ExpertRouter | None = None) -> None:
        self._router = router or ExpertRouter()

    def escalate(self, ticket: ExpertTicket) -> ExpertTicket:
        expert = self._router.route(ticket)
        ticket.assign(expert)
        logger.info("Ticket %s escalated to %s", ticket.ticket_id, expert)
        return ticket

    def should_escalate(self, confidence: float, threshold: float = 0.50) -> bool:
        return confidence < threshold

__all__ = ["EscalationService"]
