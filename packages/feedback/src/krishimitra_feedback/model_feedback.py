from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class ModelFeedbackEntry:
    model_name: str
    prediction: str
    correct: bool
    actual_label: str | None = None
    recorded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

class ModelFeedbackStore:
    def __init__(self) -> None:
        self._entries: list[ModelFeedbackEntry] = []

    def add(self, entry: ModelFeedbackEntry) -> None:
        self._entries.append(entry)

    def accuracy(self, model_name: str) -> float:
        relevant = [e for e in self._entries if e.model_name == model_name]
        if not relevant:
            return 0.0
        return sum(1 for e in relevant if e.correct) / len(relevant)

    def all_for_model(self, model_name: str) -> list[ModelFeedbackEntry]:
        return [e for e in self._entries if e.model_name == model_name]

__all__ = ["ModelFeedbackEntry", "ModelFeedbackStore"]
