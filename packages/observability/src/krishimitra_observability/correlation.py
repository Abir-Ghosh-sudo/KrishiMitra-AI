from __future__ import annotations
import uuid
from contextvars import ContextVar

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

class CorrelationId:
    @staticmethod
    def new() -> str:
        return str(uuid.uuid4())

def get_correlation_id() -> str:
    cid = _correlation_id.get()
    if not cid:
        cid = CorrelationId.new()
        _correlation_id.set(cid)
    return cid

def set_correlation_id(cid: str) -> None:
    _correlation_id.set(cid)

__all__ = ["CorrelationId", "get_correlation_id", "set_correlation_id"]
