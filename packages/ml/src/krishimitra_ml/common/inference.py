from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypeVar
from uuid import UUID, uuid4

from .features import FeatureVector
from .registry import ModelMetadata, ModelRegistry


PredictionT = TypeVar("PredictionT")


@dataclass(frozen=True, slots=True)
class InferenceRequest:
    """Input contract for a model inference operation."""

    features: FeatureVector
    request_id: UUID = uuid4()
    model_name: str | None = None
    model_version: str | None = None
    metadata: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class InferenceResult(Generic[PredictionT]):
    """Output contract for a model inference operation."""

    prediction: PredictionT
    model_name: str
    model_version: str
    request_id: UUID
    metadata: Mapping[str, Any] | None = None


class InferenceError(RuntimeError):
    """Base error raised by the inference layer."""


class ModelNotConfiguredError(InferenceError):
    """Raised when a requested model is unavailable."""


class FeatureMismatchError(InferenceError):
    """Raised when input features do not match model requirements."""


class BaseModelInference(ABC, Generic[PredictionT]):
    """
    Abstract interface for model-specific inference.

    Concrete disease, pest, irrigation, energy, crop-stage,
    and yield models implement the actual prediction logic.
    """

    @abstractmethod
    def predict(
        self,
        features: FeatureVector,
    ) -> PredictionT:
        """Generate a prediction from a feature vector."""
        raise NotImplementedError


class RegistryModelInference(
    BaseModelInference[PredictionT],
    Generic[PredictionT],
):
    """
    Generic inference adapter backed by ModelRegistry.

    The registered artifact must expose a ``predict`` method
    accepting a sequence of numeric feature values.
    """

    def __init__(
        self,
        *,
        registry: ModelRegistry,
        model_name: str,
        model_version: str | None = None,
    ) -> None:
        self._registry = registry
        self._model_name = model_name
        self._model_version = model_version

    @property
    def model_metadata(self) -> ModelMetadata:
        """Return metadata for the selected model."""

        model = self._get_registered_model()
        return model.metadata

    def predict(
        self,
        features: FeatureVector,
    ) -> PredictionT:
        """Run prediction using the registered model artifact."""

        registered_model = self._get_registered_model()

        self._validate_features(
            features,
            registered_model.metadata,
        )

        artifact = registered_model.artifact

        predict_method = getattr(
            artifact,
            "predict",
            None,
        )

        if predict_method is None:
            raise InferenceError(
                "Registered model artifact does not expose "
                "a 'predict' method."
            )

        try:
            result = predict_method(
                [list(features.values)]
            )
        except Exception as exc:
            raise InferenceError(
                "Model inference failed."
            ) from exc

        return self._unwrap_prediction(result)

    def _get_registered_model(self):
        """Resolve the requested or active model version."""

        try:
            if self._model_version is not None:
                return self._registry.get(
                    self._model_name,
                    self._model_version,
                )

            return self._registry.get_active(
                self._model_name,
            )
        except KeyError as exc:
            raise ModelNotConfiguredError(
                str(exc)
            ) from exc

    @staticmethod
    def _validate_features(
        features: FeatureVector,
        metadata: ModelMetadata,
    ) -> None:
        """Ensure model-required feature ordering is respected."""

        expected = metadata.feature_names

        if not expected:
            return

        if features.names != expected:
            raise FeatureMismatchError(
                "Feature ordering does not match the registered model. "
                f"Expected {expected}, received {features.names}."
            )

    @staticmethod
    def _unwrap_prediction(
        result: Any,
    ) -> Any:
        """
        Normalize common ML-library prediction containers.

        A single prediction is returned as a scalar where possible.
        """

        if hasattr(result, "tolist"):
            result = result.tolist()

        if isinstance(result, list) and len(result) == 1:
            return result[0]

        if isinstance(result, tuple) and len(result) == 1:
            return result[0]

        return result


class InferenceService(Generic[PredictionT]):
    """
    Application-facing inference service.

    It resolves model versions, validates feature contracts,
    executes inference, and returns traceable results.
    """

    def __init__(
        self,
        *,
        registry: ModelRegistry,
    ) -> None:
        self._registry = registry

    def predict(
        self,
        request: InferenceRequest,
    ) -> InferenceResult[PredictionT]:
        """Execute a prediction request."""

        if request.model_name is None:
            raise ModelNotConfiguredError(
                "model_name is required for inference."
            )

        model_name = request.model_name
        model_version = request.model_version

        try:
            if model_version is None:
                registered_model = self._registry.get_active(
                    model_name,
                )
            else:
                registered_model = self._registry.get(
                    model_name,
                    model_version,
                )
        except KeyError as exc:
            raise ModelNotConfiguredError(
                str(exc)
            ) from exc

        self._validate_features(
            request.features,
            registered_model.metadata,
        )

        artifact = registered_model.artifact
        predict_method = getattr(
            artifact,
            "predict",
            None,
        )

        if predict_method is None:
            raise InferenceError(
                "Registered model artifact does not expose "
                "a 'predict' method."
            )

        try:
            prediction = predict_method(
                [list(request.features.values)]
            )
        except Exception as exc:
            raise InferenceError(
                "Model inference failed."
            ) from exc

        prediction = RegistryModelInference._unwrap_prediction(
            prediction
        )

        return InferenceResult(
            prediction=prediction,
            model_name=registered_model.metadata.model_name,
            model_version=registered_model.metadata.version,
            request_id=request.request_id,
            metadata=request.metadata,
        )

    @staticmethod
    def _validate_features(
        features: FeatureVector,
        metadata: ModelMetadata,
    ) -> None:
        """Validate the request against model feature requirements."""

        expected = metadata.feature_names

        if not expected:
            return

        if features.names != expected:
            raise FeatureMismatchError(
                "Feature ordering does not match the registered model. "
                f"Expected {expected}, received {features.names}."
            )