from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Immutable configuration for a machine-learning experiment."""

    name: str
    model_name: str
    task_type: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "Experiment name cannot be empty."
            )

        if not self.model_name.strip():
            raise ValueError(
                "model_name cannot be empty."
            )

        if not self.task_type.strip():
            raise ValueError(
                "task_type cannot be empty."
            )

        if any(not tag.strip() for tag in self.tags):
            raise ValueError(
                "Experiment tags cannot be empty."
            )


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    """Recorded result of one model-training experiment."""

    experiment_id: UUID
    config: ExperimentConfig
    started_at: datetime
    completed_at: datetime
    metrics: Mapping[str, float]
    status: str
    error: str | None = None

    @property
    def duration_seconds(self) -> float:
        """Return experiment duration in seconds."""

        return max(
            0.0,
            (
                self.completed_at - self.started_at
            ).total_seconds(),
        )


class ExperimentTracker:
    """
    Lightweight experiment tracker.

    This class keeps experiment records in memory. Persistent tracking
    can later be backed by PostgreSQL or an external ML tracking
    service without changing the experiment contract.
    """

    def __init__(self) -> None:
        self._results: dict[UUID, ExperimentResult] = {}

    def start(
        self,
        config: ExperimentConfig,
    ) -> UUID:
        """Create and register a new experiment."""

        experiment_id = uuid4()

        started_at = datetime.now(
            timezone.utc
        )

        self._results[experiment_id] = ExperimentResult(
            experiment_id=experiment_id,
            config=config,
            started_at=started_at,
            completed_at=started_at,
            metrics={},
            status="running",
        )

        return experiment_id

    def complete(
        self,
        experiment_id: UUID,
        *,
        metrics: Mapping[str, float],
    ) -> ExperimentResult:
        """Mark an experiment as successfully completed."""

        current = self._get(
            experiment_id
        )

        normalized_metrics = self._validate_metrics(
            metrics
        )

        completed_at = datetime.now(
            timezone.utc
        )

        result = ExperimentResult(
            experiment_id=current.experiment_id,
            config=current.config,
            started_at=current.started_at,
            completed_at=completed_at,
            metrics=normalized_metrics,
            status="completed",
        )

        self._results[experiment_id] = result

        return result

    def fail(
        self,
        experiment_id: UUID,
        *,
        error: str,
    ) -> ExperimentResult:
        """Mark an experiment as failed."""

        if not error.strip():
            raise ValueError(
                "error cannot be empty."
            )

        current = self._get(
            experiment_id
        )

        completed_at = datetime.now(
            timezone.utc
        )

        result = ExperimentResult(
            experiment_id=current.experiment_id,
            config=current.config,
            started_at=current.started_at,
            completed_at=completed_at,
            metrics={},
            status="failed",
            error=error,
        )

        self._results[experiment_id] = result

        return result

    def get(
        self,
        experiment_id: UUID,
    ) -> ExperimentResult:
        """Return an experiment result."""

        return self._get(
            experiment_id
        )

    def list(
        self,
    ) -> tuple[ExperimentResult, ...]:
        """Return all tracked experiments."""

        return tuple(
            self._results.values()
        )

    def clear(self) -> None:
        """Clear in-memory experiment records."""

        self._results.clear()

    def _get(
        self,
        experiment_id: UUID,
    ) -> ExperimentResult:
        try:
            return self._results[experiment_id]
        except KeyError as exc:
            raise KeyError(
                f"Experiment not found: {experiment_id}"
            ) from exc

    @staticmethod
    def _validate_metrics(
        metrics: Mapping[str, float],
    ) -> dict[str, float]:
        from math import isfinite

        normalized: dict[str, float] = {}

        for name, value in metrics.items():
            metric_name = str(name).strip()

            if not metric_name:
                raise ValueError(
                    "Metric names cannot be empty."
                )

            numeric_value = float(value)

            if not isfinite(numeric_value):
                raise ValueError(
                    f"Metric '{metric_name}' must be finite."
                )

            normalized[metric_name] = numeric_value

        return normalized


__all__ = [
    "ExperimentConfig",
    "ExperimentResult",
    "ExperimentTracker",
]