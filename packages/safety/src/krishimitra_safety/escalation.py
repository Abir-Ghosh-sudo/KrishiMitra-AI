from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

class SafetyEscalation:
    def escalate(self, violation: str, farmer_id: str) -> None:
        logger.warning("SAFETY ESCALATION farmer=%s violation=%s", farmer_id, violation)

    def should_block_response(self, severity: str) -> bool:
        return severity in ("critical", "error")

__all__ = ["SafetyEscalation"]
