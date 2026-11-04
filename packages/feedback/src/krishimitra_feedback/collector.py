from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum

class Rating(IntEnum):
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5

@dataclass
class FeedbackRecord:
    farmer_id: str
    session_id: str
    rating: Rating
    comment: str = ""
    recommendation_id: str | None = None
    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

class FeedbackCollector:
    def __init__(self) -> None:
        self._records: list[FeedbackRecord] = []

    def collect(self, record: FeedbackRecord) -> None:
        self._records.append(record)

    def all(self) -> list[FeedbackRecord]:
        return list(self._records)

    def average_rating(self) -> float:
        if not self._records:
            return 0.0
        return sum(r.rating for r in self._records) / len(self._records)

__all__ = ["FeedbackCollector", "FeedbackRecord", "Rating"]
