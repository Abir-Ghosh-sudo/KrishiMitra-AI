"""Generic inference service base used by all ML sub-modules.

Provides a thin, framework-agnostic wrapper around any fitted model
that exposes a sklearn-compatible interface (predict / predict_proba).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

__all__ = [
    "BaseModelInference",
    "FeatureMismatchError",
    "InferenceError",
    "InferenceRequest",
    "InferenceResult",
    "InferenceService",
    "ModelAdapter",
    "ModelNotConfiguredError",
    "RegistryModelInference",
]

logger = logging.getLogger(__name__)


class InferenceError(RuntimeError):
    """Raised when model inference produces an invalid result."""


class FeatureMismatchError(InferenceError):
    """Raised when supplied features do not match the model schema."""


class ModelNotConfiguredError(InferenceError):
    """Raised when an inference service is used before a model is set."""


@dataclass(frozen=True, slots=True)
class ModelAdapter:
    """Thin wrapper carrying a fitted model and its display name."""

    model: object
    model_name: str
    version: str = "1.0.0"

    def predict(self, X: Any) -> Any:
        if not hasattr(self.model, "predict"):
            raise InferenceError(f"{self.model_name} does not expose predict().")
        try:
            return self.model.predict(X)
        except Exception as exc:
            raise InferenceError(f"predict() failed in {self.model_name}: {exc}") from exc

    def predict_proba(self, X: Any) -> Any | None:
        fn = getattr(self.model, "predict_proba", None)
        if fn is None:
            return None
        try:
            return fn(X)
        except Exception as exc:
            raise InferenceError(
                f"predict_proba() failed in {self.model_name}: {exc}"
            ) from exc


class InferenceService:
    """Protocol-agnostic inference service for tabular feature vectors.

    The service is deliberately decoupled from any specific algorithm.
    Inject any sklearn-compatible estimator (RandomForest, XGBoost, etc.)
    and the service handles the input/output contract.

    Parameters
    ----------
    model:
        Fitted estimator exposing predict() and optionally predict_proba().
    model_name:
        Descriptive name used in logs and error messages.
    feature_names:
        Ordered feature names the model was trained on.
        Used to validate inputs and reorder feature vectors.
    version:
        Semantic version string of the model artifact.
    """

    def __init__(
        self,
        model: object,
        *,
        model_name: str,
        feature_names: Sequence[str],
        version: str = "1.0.0",
    ) -> None:
        if not feature_names:
            raise ValueError("feature_names cannot be empty.")
        self._adapter = ModelAdapter(
            model=model,
            model_name=model_name,
            version=version,
        )
        self._feature_names: tuple[str, ...] = tuple(feature_names)

    @property
    def model_name(self) -> str:
        return self._adapter.model_name

    @property
    def version(self) -> str:
        return self._adapter.version

    @property
    def feature_names(self) -> tuple[str, ...]:
        return self._feature_names

    def run(
        self,
        features: Sequence[Sequence[float]],
    ) -> tuple[Any, ...]:
        """Run inference and return raw model outputs as a tuple.

        Parameters
        ----------
        features:
            2-D sequence (n_samples × n_features) of numeric values
            in the same order as :attr:`feature_names`.

        Returns
        -------
        tuple
            Raw model outputs, one element per sample.
        """
        self._validate_input(features)
        raw = self._adapter.predict(features)
        return self._to_tuple(raw)

    def run_proba(
        self,
        features: Sequence[Sequence[float]],
    ) -> tuple[tuple[float, ...], ...] | None:
        """Run probabilistic inference if the model supports it.

        Returns *None* when the underlying model does not expose
        ``predict_proba``.
        """
        self._validate_input(features)
        raw = self._adapter.predict_proba(features)
        if raw is None:
            return None
        if hasattr(raw, "tolist"):
            raw = raw.tolist()
        return tuple(tuple(float(p) for p in row) for row in raw)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate_input(
        self,
        features: Sequence[Sequence[float]],
    ) -> None:
        if not features:
            raise InferenceError("features cannot be empty.")
        n_expected = len(self._feature_names)
        for i, row in enumerate(features):
            if len(row) != n_expected:
                raise InferenceError(
                    f"Row {i}: expected {n_expected} features, got {len(row)}."
                )

    @staticmethod
    def _to_tuple(raw: Any) -> tuple[Any, ...]:
        if hasattr(raw, "tolist"):
            raw = raw.tolist()
        if isinstance(raw, (list, tuple)):
            return tuple(raw)
        return (raw,)


@dataclass(frozen=True, slots=True)
class InferenceRequest:
    """A single inference request carrying feature rows."""

    features: tuple[tuple[float, ...], ...]
    feature_names: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.feature_names:
            raise FeatureMismatchError("feature_names cannot be empty.")

        if not self.features:
            raise FeatureMismatchError("features cannot be empty.")

        expected_width = len(self.feature_names)

        for index, row in enumerate(self.features):
            if len(row) != expected_width:
                raise FeatureMismatchError(
                    f"Row {index}: expected {expected_width} features, "
                    f"got {len(row)}."
                )

            if not all(
                isinstance(value, (int, float))
                and value == value
                and abs(value) != float("inf")
                for value in row
            ):
                raise FeatureMismatchError(
                    f"Row {index}: features must be finite numeric values."
                )


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """A single inference result paired with the source request id."""

    request_id: str
    predictions: tuple[Any, ...]
    probabilities: tuple[tuple[float, ...], ...] | None = None

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("request_id cannot be empty.")

        if not self.probabilities:
            self.probabilities = None


class BaseModelInference:
    """
    Base class for model-backed inference services.

    Subclasses configure a concrete model and feature schema. The base
    class is intentionally framework-agnostic and validates the input
    contract before delegating to the wrapped model.
    """

    def __init__(
        self,
        *,
        model: object,
        model_name: str,
        feature_names: Sequence[str],
        version: str = "1.0.0",
    ) -> None:
        if model is None:
            raise ModelNotConfiguredError(
                "A model must be provided to BaseModelInference."
            )

        if not hasattr(model, "predict"):
            raise ModelNotConfiguredError(
                "Configured model does not expose predict()."
            )

        normalized_names = tuple(
            str(name).strip() for name in feature_names
        )

        if not normalized_names:
            raise FeatureMismatchError("feature_names cannot be empty.")

        if any(not name for name in normalized_names):
            raise FeatureMismatchError(
                "feature_names cannot contain empty entries."
            )

        if len(set(normalized_names)) != len(normalized_names):
            raise FeatureMismatchError(
                "feature_names must be unique."
            )

        self._model = model
        self._model_name = model_name.strip()
        self._feature_names = normalized_names
        self._version = version.strip()

    @property
    def model_name(self) -> str:
        """Return the configured model name."""

        return self._model_name

    @property
    def version(self) -> str:
        """Return the configured model version."""

        return self._version

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return the ordered feature names the model expects."""

        return self._feature_names

    def infer(self, request: InferenceRequest) -> InferenceResult:
        """Run inference for a validated request."""

        self._validate_request(request)

        try:
            raw_predictions = self._model.predict(
                request.features
            )
        except Exception as exc:
            raise InferenceError(
                f"Model '{self._model_name}' prediction failed: {exc}"
            ) from exc

        predictions = self._to_tuple(raw_predictions)

        probabilities = self._predict_proba(
            request.features
        )

        return InferenceResult(
            request_id=self._request_id(),
            predictions=predictions,
            probabilities=probabilities,
        )

    def infer_from_values(
        self,
        features: Sequence[Sequence[float]],
    ) -> InferenceResult:
        """Convenience wrapper that builds a request from raw values."""

        request = InferenceRequest(
            features=tuple(
                tuple(float(value) for value in row)
                for row in features
            ),
            feature_names=self._feature_names,
        )

        return self.infer(request)

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def _validate_request(
        self,
        request: InferenceRequest,
    ) -> None:
        if request.feature_names != self._feature_names:
            raise FeatureMismatchError(
                "Request feature names do not match the model schema."
            )

    def _predict_proba(
        self,
        features: Sequence[Sequence[float]],
    ) -> tuple[tuple[float, ...], ...] | None:
        predict_proba = getattr(self._model, "predict_proba", None)

        if predict_proba is None:
            return None

        try:
            raw = predict_proba(features)
        except Exception as exc:
            raise InferenceError(
                f"predict_proba() failed in '{self._model_name}': {exc}"
            ) from exc

        if hasattr(raw, "tolist"):
            raw = raw.tolist()

        return tuple(
            tuple(float(value) for value in row)
            for row in raw
        )

    @staticmethod
    def _to_tuple(raw: Any) -> tuple[Any, ...]:
        if hasattr(raw, "tolist"):
            raw = raw.tolist()
        if isinstance(raw, (list, tuple)):
            return tuple(raw)
        return (raw,)

    @staticmethod
    def _request_id() -> str:
        from uuid import uuid4

        return uuid4().hex


class RegistryModelInference(BaseModelInference):
    """
    Inference service backed by a model pulled from a ModelRegistry.

    The registry supplies both the artifact and its metadata. The
    service remains decoupled from any specific registry backend.
    """

    def __init__(
        self,
        registry: Any,
        model_name: str,
        *,
        version: str | None = None,
    ) -> None:
        if registry is None:
            raise ModelNotConfiguredError(
                "A model registry is required for RegistryModelInference."
            )

        if not hasattr(registry, "get") or not hasattr(registry, "get_active"):
            raise ModelNotConfiguredError(
                "Registry must expose get() and get_active()."
            )

        registered = (
            registry.get(model_name, version)
            if version is not None
            else registry.get_active(model_name)
        )

        metadata = registered.metadata
        artifact = registered.artifact

        super().__init__(
            model=artifact,
            model_name=metadata.model_name,
            feature_names=metadata.feature_names,
            version=metadata.version,
        )

        self._registry = registry

    @property
    def registry(self) -> Any:
        """Return the backing registry."""

        return self._registry