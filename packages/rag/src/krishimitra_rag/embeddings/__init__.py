"""Embedding generation and model abstractions for KrishiMitra-AI RAG."""

from .generator import (
    EmbeddingBatch,
    EmbeddingGenerationError,
    EmbeddingGenerator,
    GeneratedEmbedding,
    cosine_similarity,
)
from .model import (
    EmbeddingModel,
    EmbeddingModelError,
    EmbeddingModelInfo,
    EmbeddingModelValidator,
    ValidatedEmbeddingModel,
)

__all__ = [
    "EmbeddingBatch",
    "EmbeddingGenerationError",
    "EmbeddingGenerator",
    "EmbeddingModel",
    "EmbeddingModelError",
    "EmbeddingModelInfo",
    "EmbeddingModelValidator",
    "GeneratedEmbedding",
    "ValidatedEmbeddingModel",
    "cosine_similarity",
]