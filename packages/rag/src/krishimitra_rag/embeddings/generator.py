from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .model import (
    EmbeddingModelError,
    ValidatedEmbeddingModel,
)


class EmbeddingGenerationError(RuntimeError):
    """Raised when embedding generation fails."""


@dataclass(frozen=True, slots=True)
class GeneratedEmbedding:
    """Embedding generated for a single text."""

    text: str
    vector: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class EmbeddingBatch:
    """A validated batch of generated embeddings."""

    items: tuple[GeneratedEmbedding, ...]
    model_name: str
    dimension: int


class EmbeddingGenerator:
    """Generates validated embeddings through an injected embedding model."""

    def __init__(self, model: ValidatedEmbeddingModel) -> None:
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model.info.name

    @property
    def dimension(self) -> int:
        return self._model.info.dimension

    def generate(self, text: str) -> GeneratedEmbedding:
        """Generate an embedding for one text."""
        if not isinstance(text, str):
            raise EmbeddingGenerationError(
                "Text must be a string"
            )

        normalized = text.strip()

        if not normalized:
            raise EmbeddingGenerationError(
                "Text cannot be empty"
            )

        try:
            vectors = self._model.encode([normalized])
        except EmbeddingModelError as exc:
            raise EmbeddingGenerationError(
                "Unable to generate embedding"
            ) from exc

        if len(vectors) != 1:
            raise EmbeddingGenerationError(
                "Embedding model returned an invalid result"
            )

        vector = tuple(float(value) for value in vectors[0])

        return GeneratedEmbedding(
            text=normalized,
            vector=vector,
        )

    def generate_batch(self, texts: list[str]) -> EmbeddingBatch:
        """Generate embeddings for multiple texts."""
        if not isinstance(texts, list):
            raise EmbeddingGenerationError(
                "Texts must be provided as a list"
            )

        if not texts:
            return EmbeddingBatch(
                items=(),
                model_name=self.model_name,
                dimension=self.dimension,
            )

        normalized_texts: list[str] = []

        for index, text in enumerate(texts):
            if not isinstance(text, str):
                raise EmbeddingGenerationError(
                    f"Text at index {index} must be a string"
                )

            normalized = text.strip()

            if not normalized:
                raise EmbeddingGenerationError(
                    f"Text at index {index} cannot be empty"
                )

            normalized_texts.append(normalized)

        try:
            vectors = self._model.encode(normalized_texts)
        except EmbeddingModelError as exc:
            raise EmbeddingGenerationError(
                "Unable to generate embedding batch"
            ) from exc

        if len(vectors) != len(normalized_texts):
            raise EmbeddingGenerationError(
                "Embedding count does not match input count"
            )

        items = tuple(
            GeneratedEmbedding(
                text=text,
                vector=tuple(float(value) for value in vector),
            )
            for text, vector in zip(
                normalized_texts,
                vectors,
                strict=True,
            )
        )

        return EmbeddingBatch(
            items=items,
            model_name=self.model_name,
            dimension=self.dimension,
        )


def cosine_similarity(
    first: tuple[float, ...],
    second: tuple[float, ...],
) -> float:
    """Calculate cosine similarity between two embeddings."""
    if not first or not second:
        raise EmbeddingGenerationError(
            "Embeddings cannot be empty"
        )

    if len(first) != len(second):
        raise EmbeddingGenerationError(
            "Embeddings must have the same dimension"
        )

    first_norm = sqrt(sum(value * value for value in first))
    second_norm = sqrt(sum(value * value for value in second))

    if first_norm == 0 or second_norm == 0:
        raise EmbeddingGenerationError(
            "Zero-vector embeddings cannot be compared"
        )

    similarity = sum(
        left * right
        for left, right in zip(first, second, strict=True)
    ) / (first_norm * second_norm)

    return max(-1.0, min(1.0, similarity))


__all__ = [
    "EmbeddingBatch",
    "EmbeddingGenerationError",
    "EmbeddingGenerator",
    "GeneratedEmbedding",
    "cosine_similarity",
]