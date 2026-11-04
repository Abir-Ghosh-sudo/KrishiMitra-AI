from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from contextlib import contextmanager
from typing import Generator

@dataclass
class Span:
    operation: str
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = field(default_factory=time.monotonic)
    end_time: float | None = None
    tags: dict[str, str] = field(default_factory=dict)

    def finish(self) -> None:
        self.end_time = time.monotonic()

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000

class Tracer:
    @contextmanager
    def start_span(self, operation: str) -> Generator[Span, None, None]:
        span = Span(operation=operation)
        try:
            yield span
        finally:
            span.finish()

__all__ = ["Span", "Tracer"]
