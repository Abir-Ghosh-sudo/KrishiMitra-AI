from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .retriever import RetrievalResult


class RerankingError(RuntimeError):
    """Raised when retrieval result reranking fails."""


@dataclass(frozen=True, slots=True)
class RerankedResult:
    """A retrieval result with its reranking score."""

    chunk_id: str
    text: str
    retrieval_score: float
    rerank_score: float
    document_id: object | None = None
    source: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()


class RerankerBackend(Protocol):
    """Backend contract for model-based reranking."""

    def score(
        self,
        query: str,
        documents: list[str],
    ) -> list[float]:
        """Return one relevance score for each document."""


class SemanticReranker:
    """Reranks retrieved results using an injected relevance backend."""

    def __init__(
        self,
        backend: RerankerBackend | None = None,
        *,
        top_k: int | None = None,
    ) -> None:
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        self._backend = backend
        self._top_k = top_k

    def rerank(
        self,
        query: str,
        results: tuple[RetrievalResult, ...],
    ) -> tuple[RerankedResult, ...]:
        if not isinstance(query, str):
            raise RerankingError("Query must be a string")

        normalized_query = query.strip()

        if not normalized_query:
            raise RerankingError("Query cannot be empty")

        if not results:
            return ()

        if self._backend is None:
            return self._fallback_rerank(results)

        documents = [result.text for result in results]

        try:
            scores = self._backend.score(
                normalized_query,
                documents,
            )
        except Exception as exc:
            raise RerankingError(
                "Reranking backend failed"
            ) from exc

        if len(scores) != len(results):
            raise RerankingError(
                "Reranking backend returned an invalid score count"
            )

        reranked: list[RerankedResult] = []

        for result, score in zip(
            results,
            scores,
            strict=True,
        ):
            if not isinstance(score, (int, float)):
                raise RerankingError(
                    "Reranking scores must be numeric"
                )

            reranked.append(
                RerankedResult(
                    chunk_id=result.chunk_id,
                    text=result.text,
                    retrieval_score=result.score,
                    rerank_score=float(score),
                    document_id=result.document_id,
                    source=result.source,
                    metadata=result.metadata,
                )
            )

        reranked.sort(
            key=lambda item: (
                -item.rerank_score,
                -item.retrieval_score,
                item.chunk_id,
            )
        )

        if self._top_k is not None:
            reranked = reranked[: self._top_k]

        return tuple(reranked)

    def _fallback_rerank(
        self,
        results: tuple[RetrievalResult, ...],
    ) -> tuple[RerankedResult, ...]:
        """Use retrieval similarity when no reranking model is configured."""

        reranked = tuple(
            RerankedResult(
                chunk_id=result.chunk_id,
                text=result.text,
                retrieval_score=result.score,
                rerank_score=result.score,
                document_id=result.document_id,
                source=result.source,
                metadata=result.metadata,
            )
            for result in results
        )

        if self._top_k is None:
            return reranked

        return reranked[: self._top_k]


__all__ = [
    "RerankedResult",
    "RerankerBackend",
    "RerankingError",
    "SemanticReranker",
]