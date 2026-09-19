from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    """Immutable metadata describing a registered ML model."""

    model_name: str
    version: str
    model_type: str
    artifact_uri: str | None = None
    feature_names: tuple[str, ...] = ()
    metrics: Mapping[str, float] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    description: str = ""

    def __post_init__(self) -> None:
        if not self.model_name.strip():
            raise ValueError("model_name cannot be empty.")

        if not self.version.strip():
            raise ValueError("version cannot be empty.")

        if not self.model_type.strip():
            raise ValueError("model_type cannot be empty.")

        if self.created_at.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )

        if len(set(self.feature_names)) != len(self.feature_names):
            raise ValueError(
                "feature_names must contain unique values."
            )

        for name in self.feature_names:
            if not name.strip():
                raise ValueError(
                    "feature_names cannot contain empty names."
                )

        for metric_name, metric_value in self.metrics.items():
            if not metric_name.strip():
                raise ValueError(
                    "Metric names cannot be empty."
                )

            if not isinstance(metric_value, (int, float)):
                raise TypeError(
                    f"Metric '{metric_name}' must be numeric."
                )


@dataclass(frozen=True, slots=True)
class RegisteredModel:
    """A model together with its immutable metadata."""

    metadata: ModelMetadata
    artifact: Any


class ModelRegistry:
    """
    Thread-safe in-process model registry.

    The registry provides deterministic model lookup and versioning
    semantics. Persistent storage and artifact management belong to
    the production model infrastructure layer.
    """

    def __init__(self) -> None:
        self._models: dict[
            tuple[str, str],
            RegisteredModel,
        ] = {}
        self._active_versions: dict[str, str] = {}
        self._lock = RLock()

    def register(
        self,
        *,
        metadata: ModelMetadata,
        artifact: Any,
        activate: bool = False,
    ) -> RegisteredModel:
        """Register a model version."""

        key = (
            metadata.model_name,
            metadata.version,
        )

        with self._lock:
            if key in self._models:
                raise ValueError(
                    "Model version is already registered: "
                    f"{metadata.model_name}@{metadata.version}"
                )

            registered = RegisteredModel(
                metadata=metadata,
                artifact=artifact,
            )

            self._models[key] = registered

            if activate:
                self._active_versions[
                    metadata.model_name
                ] = metadata.version

            return registered

    def activate(
        self,
        model_name: str,
        version: str,
    ) -> RegisteredModel:
        """Mark an existing model version as active."""

        with self._lock:
            model = self.get(
                model_name,
                version,
            )

            self._active_versions[model_name] = version

            return model

    def get(
        self,
        model_name: str,
        version: str,
    ) -> RegisteredModel:
        """Retrieve an exact model version."""

        key = (
            model_name,
            version,
        )

        with self._lock:
            try:
                return self._models[key]
            except KeyError as exc:
                raise KeyError(
                    f"Model not found: {model_name}@{version}"
                ) from exc

    def get_active(
        self,
        model_name: str,
    ) -> RegisteredModel:
        """Retrieve the currently active model version."""

        with self._lock:
            try:
                version = self._active_versions[
                    model_name
                ]
            except KeyError as exc:
                raise KeyError(
                    f"No active model registered for '{model_name}'."
                ) from exc

            return self.get(
                model_name,
                version,
            )

    def is_registered(
        self,
        model_name: str,
        version: str,
    ) -> bool:
        """Check whether an exact model version exists."""

        with self._lock:
            return (
                model_name,
                version,
            ) in self._models

    def is_active(
        self,
        model_name: str,
        version: str,
    ) -> bool:
        """Check whether a specific version is active."""

        with self._lock:
            return (
                self._active_versions.get(model_name)
                == version
            )

    def list_versions(
        self,
        model_name: str,
    ) -> tuple[str, ...]:
        """Return all registered versions for a model."""

        with self._lock:
            versions = [
                version
                for name, version in self._models
                if name == model_name
            ]

            return tuple(sorted(versions))

    def list_models(self) -> tuple[ModelMetadata, ...]:
        """Return metadata for all registered model versions."""

        with self._lock:
            return tuple(
                model.metadata
                for model in self._models.values()
            )

    def unregister(
        self,
        model_name: str,
        version: str,
    ) -> None:
        """Remove a model version from the in-process registry."""

        key = (
            model_name,
            version,
        )

        with self._lock:
            if key not in self._models:
                raise KeyError(
                    f"Model not found: {model_name}@{version}"
                )

            del self._models[key]

            if self._active_versions.get(model_name) == version:
                del self._active_versions[model_name]

    def clear(self) -> None:
        """Clear all registered models."""

        with self._lock:
            self._models.clear()
            self._active_versions.clear()