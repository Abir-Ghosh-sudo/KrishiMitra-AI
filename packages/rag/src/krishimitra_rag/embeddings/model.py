from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class EmbeddingModelError(RuntimeError):
    """Raised when an embedding model operation fails."""


@dataclass(frozen=True, slots=True)
class EmbeddingModelInfo:
    """Metadata describing an embedding model."""

    name: str
    dimension: int
    version: str = "1.0"
    provider: str = "local"


class EmbeddingModel(Protocol):
    """Backend contract for generating vector embeddings."""

    @property
    def info(self) -> EmbeddingModelInfo:
        """Return embedding model metadata."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""


class EmbeddingModelValidator:
    """Validates embedding model metadata and generated vectors."""

    @staticmethod
    def validate_info(info: EmbeddingModelInfo) -> EmbeddingModelInfo:
        if not isinstance(info, EmbeddingModelInfo):
            raise EmbeddingModelError(
                "Embedding model must provide EmbeddingModelInfo"
            )

        if not info.name.strip():
            raise EmbeddingModelError(
                "Embedding model name cannot be empty"
            )

        if info.dimension <= 0:
            raise EmbeddingModelError(
                "Embedding dimension must be greater than zero"
            )

        if not info.version.strip():
            raise EmbeddingModelError(
                "Embedding model version cannot be empty"
            )

        if not info.provider.strip():
            raise EmbeddingModelError(
                "Embedding model provider cannot be empty"
            )

        return info

    @staticmethod
    def validate_vectors(
        vectors: list[list[float]],
        *,
        expected_count: int,
        expected_dimension: int,
    ) -> list[list[float]]:
        if not isinstance(vectors, list):
            raise EmbeddingModelError(
                "Embedding backend must return a list"
            )

        if len(vectors) != expected_count:
            raise EmbeddingModelError(
                "Embedding count does not match input count"
            )

        for index, vector in enumerate(vectors):
            if not isinstance(vector, list):
                raise EmbeddingModelError(
                    f"Embedding at index {index} is not a list"
                )

            if len(vector) != expected_dimension:
                raise EmbeddingModelError(
                    f"Embedding at index {index} has dimension "
                    f"{len(vector)}, expected {expected_dimension}"
                )

            if not all(isinstance(value, (int, float)) for value in vector):
                raise EmbeddingModelError(
                    f"Embedding at index {index} contains non-numeric values"
                )

        return vectors


class ValidatedEmbeddingModel:
    """Wraps an embedding backend with strict input/output validation."""

    def __init__(self, backend: EmbeddingModel) -> None:
        self._backend = backend

        try:
            info = backend.info
        except Exception as exc:
            raise EmbeddingModelError(
                "Unable to read embedding model metadata"
            ) from exc

        self._info = EmbeddingModelValidator.validate_info(info)

    @property
    def info(self) -> EmbeddingModelInfo:
        return self._info

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not isinstance(texts, list):
            raise EmbeddingModelError(
                "Embedding input must be a list of strings"
            )

        normalized_texts: list[str] = []

        for index, text in enumerate(texts):
            if not isinstance(text, str):
                raise EmbeddingModelError(
                    f"Embedding input at index {index} must be a string"
                )

            normalized = text.strip()

            if not normalized:
                raise EmbeddingModelError(
                    f"Embedding input at index {index} cannot be empty"
                )

            normalized_texts.append(normalized)

        if not normalized_texts:
            return []

        try:
            vectors = self._backend.encode(normalized_texts)
        except EmbeddingModelError:
            raise
        except Exception as exc:
            raise EmbeddingModelError(
                f"Embedding generation failed for model {self._info.name}"
            ) from exc

        return EmbeddingModelValidator.validate_vectors(
            vectors,
            expected_count=len(normalized_texts),
            expected_dimension=self._info.dimension,
        )


__all__ = [
    "EmbeddingModel",
    "EmbeddingModelError",
    "EmbeddingModelInfo",
    "EmbeddingModelValidator",
    "ValidatedEmbeddingModel",
]