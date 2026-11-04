from __future__ import annotations
from .ticket import ExpertTicket, TicketPriority

_SPECIALIZATIONS: dict[str, list[str]] = {
    "disease": ["plant_pathologist", "agronomist"],
    "pest": ["entomologist", "agronomist"],
    "soil": ["soil_scientist", "agronomist"],
    "weather": ["agro_meteorologist"],
    "irrigation": ["irrigation_engineer", "agronomist"],
}

class ExpertRouter:
    def route(self, ticket: ExpertTicket) -> str:
        candidates = _SPECIALIZATIONS.get(ticket.issue_type, ["agronomist"])
        return candidates[0]

__all__ = ["ExpertRouter"]
