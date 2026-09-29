from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Protocol
from uuid import UUID


class RetrievalError(RuntimeError):
    """Raised when RAG retrieval fails."""


@dataclass(frozen=True, slots=True)
class RetrievalDocument:
    """A document chunk available for semantic retrieval."""

    chunk_id: str
    text: str
    embedding: tuple[float, ...]
    document_id: UUID | None = None
    source: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """A retrieved document with its similarity score."""

    chunk_id: str
    text: str
    score: float
    document_id: UUID | None = None
    source: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()


class VectorStore(Protocol):
    """Backend contract for vector similarity search."""

    def search(
        self,
        query_embedding: tuple[float, ...],
        *,
        top_k: int,
    ) -> list[RetrievalDocument]:
        """Return candidate documents for a query embedding."""


class InMemoryVectorStore:
    """Small deterministic vector store useful for local execution and tests."""

    def __init__(
        self,
        documents: list[RetrievalDocument] | None = None,
    ) -> None:
        self._documents = list(documents or [])

    def add(self, document: RetrievalDocument) -> None:
        self._validate_document(document)
        self._documents.append(document)

    def add_many(self, documents: list[RetrievalDocument]) -> None:
        for document in documents:
            self.add(document)

    def search(
        self,
        query_embedding: tuple[float, ...],
        *,
        top_k: int,
    ) -> list[RetrievalDocument]:
        if not query_embedding:
            raise RetrievalError("Query embedding cannot be empty")

        if top_k <= 0:
            raise RetrievalError("top_k must be greater than zero")

        scored: list[tuple[float, RetrievalDocument]] = []

        for document in self._documents:
            if len(document.embedding) != len(query_embedding):
                continue

            score = _cosine_similarity(
                query_embedding,
                document.embedding,
            )

            scored.append((score, document))

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].chunk_id,
            )
        )

        return [
            document
            for _, document in scored[:top_k]
        ]

    @staticmethod
    def _validate_document(document: RetrievalDocument) -> None:
        if not isinstance(document, RetrievalDocument):
            raise RetrievalError(
                "Vector store accepts RetrievalDocument instances only"
            )

        if not document.chunk_id.strip():
            raise RetrievalError(
                "Document chunk_id cannot be empty"
            )

        if not document.text.strip():
            raise RetrievalError(
                "Document text cannot be empty"
            )

        if not document.embedding:
            raise RetrievalError(
                "Document embedding cannot be empty"
            )

        if not all(
            isinstance(value, (int, float))
            for value in document.embedding
        ):
            raise RetrievalError(
                "Document embedding must contain numeric values"
            )


class SemanticRetriever:
    """Retrieves knowledge using vector similarity."""

    def __init__(
        self,
        vector_store: VectorStore,
        *,
        top_k: int = 5,
        minimum_score: float = -1.0,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        if not -1.0 <= minimum_score <= 1.0:
            raise ValueError(
                "minimum_score must be between -1 and 1"
            )

        self._vector_store = vector_store
        self._top_k = top_k
        self._minimum_score = minimum_score

    def retrieve(
        self,
        query_embedding: tuple[float, ...],
    ) -> tuple[RetrievalResult, ...]:
        if not query_embedding:
            raise RetrievalError(
                "Query embedding cannot be empty"
            )

        try:
            documents = self._vector_store.search(
                query_embedding,
                top_k=self._top_k,
            )
        except RetrievalError:
            raise
        except Exception as exc:
            raise RetrievalError(
                "Vector retrieval failed"
            ) from exc

        results: list[RetrievalResult] = []

        for document in documents:
            if len(document.embedding) != len(query_embedding):
                continue

            score = _cosine_similarity(
                query_embedding,
                document.embedding,
            )

            if score < self._minimum_score:
                continue

            results.append(
                RetrievalResult(
                    chunk_id=document.chunk_id,
                    text=document.text,
                    score=score,
                    document_id=document.document_id,
                    source=document.source,
                    metadata=document.metadata,
                )
            )

        results.sort(
            key=lambda result: (
                -result.score,
                result.chunk_id,
            )
        )

        return tuple(results)


def _cosine_similarity(
    first: tuple[float, ...],
    second: tuple[float, ...],
) -> float:
    if len(first) != len(second):
        raise RetrievalError(
            "Embeddings must have the same dimension"
        )

    first_norm = sqrt(
        sum(value * value for value in first)
    )
    second_norm = sqrt(
        sum(value * value for value in second)
    )

    if first_norm == 0 or second_norm == 0:
        raise RetrievalError(
            "Zero-vector embeddings cannot be compared"
        )

    similarity = sum(
        left * right
        for left, right in zip(first, second, strict=True)
    ) / (first_norm * second_norm)

    return max(-1.0, min(1.0, similarity))


__all__ = [
    "InMemoryVectorStore",
    "RetrievalDocument",
    "RetrievalError",
    "RetrievalResult",
    "SemanticRetriever",
    "VectorStore",
]