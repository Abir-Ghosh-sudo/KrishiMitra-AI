from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .reranker import RerankedResult, SemanticReranker
from .retriever import RetrievalResult, SemanticRetriever


class HybridRetrievalError(RuntimeError):
    """Raised when hybrid retrieval fails."""


@dataclass(frozen=True, slots=True)
class HybridRetrievalResult:
    """Final result produced by hybrid retrieval."""

    chunk_id: str
    text: str
    semantic_score: float
    rerank_score: float
    final_score: float
    document_id: object | None = None
    source: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()


class KeywordRetriever(Protocol):
    """Backend contract for lexical retrieval."""

    def retrieve(
        self,
        query: str,
        *,
        top_k: int,
    ) -> tuple[RetrievalResult, ...]:
        """Return lexical retrieval candidates."""


class SimpleKeywordRetriever:
    """Deterministic lexical retriever for local use and testing."""

    def __init__(
        self,
        documents: tuple[RetrievalResult, ...] = (),
    ) -> None:
        self._documents = documents

    def retrieve(
        self,
        query: str,
        *,
        top_k: int,
    ) -> tuple[RetrievalResult, ...]:
        if not isinstance(query, str):
            raise HybridRetrievalError(
                "Query must be a string"
            )

        normalized_query = query.strip().lower()

        if not normalized_query:
            raise HybridRetrievalError(
                "Query cannot be empty"
            )

        if top_k <= 0:
            raise HybridRetrievalError(
                "top_k must be greater than zero"
            )

        query_terms = {
            term
            for term in normalized_query.split()
            if term
        }

        scored: list[RetrievalResult] = []

        for document in self._documents:
            document_terms = {
                term
                for term in document.text.lower().split()
                if term
            }

            if not document_terms:
                continue

            overlap = len(query_terms & document_terms)

            if overlap == 0:
                continue

            score = overlap / len(query_terms)

            scored.append(
                RetrievalResult(
                    chunk_id=document.chunk_id,
                    text=document.text,
                    score=score,
                    document_id=document.document_id,
                    source=document.source,
                    metadata=document.metadata,
                )
            )

        scored.sort(
            key=lambda result: (
                -result.score,
                result.chunk_id,
            )
        )

        return tuple(scored[:top_k])


class HybridRetriever:
    """Combines semantic and lexical retrieval before reranking."""

    def __init__(
        self,
        semantic_retriever: SemanticRetriever,
        *,
        keyword_retriever: KeywordRetriever | None = None,
        reranker: SemanticReranker | None = None,
        semantic_weight: float = 0.7,
        lexical_weight: float = 0.3,
        candidate_multiplier: int = 2,
        top_k: int = 5,
    ) -> None:
        if semantic_weight < 0:
            raise ValueError(
                "semantic_weight cannot be negative"
            )

        if lexical_weight < 0:
            raise ValueError(
                "lexical_weight cannot be negative"
            )

        if semantic_weight + lexical_weight <= 0:
            raise ValueError(
                "At least one retrieval weight must be greater than zero"
            )

        if candidate_multiplier <= 0:
            raise ValueError(
                "candidate_multiplier must be greater than zero"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

        self._semantic_retriever = semantic_retriever
        self._keyword_retriever = keyword_retriever
        self._reranker = reranker

        total_weight = semantic_weight + lexical_weight

        self._semantic_weight = semantic_weight / total_weight
        self._lexical_weight = lexical_weight / total_weight

        self._candidate_multiplier = candidate_multiplier
        self._top_k = top_k

    def retrieve(
        self,
        query: str,
        query_embedding: tuple[float, ...],
    ) -> tuple[HybridRetrievalResult, ...]:
        if not isinstance(query, str):
            raise HybridRetrievalError(
                "Query must be a string"
            )

        normalized_query = query.strip()

        if not normalized_query:
            raise HybridRetrievalError(
                "Query cannot be empty"
            )

        candidate_k = self._top_k * self._candidate_multiplier

        try:
            semantic_results = self._semantic_retriever.retrieve(
                query_embedding
            )

            lexical_results = (
                self._keyword_retriever.retrieve(
                    normalized_query,
                    top_k=candidate_k,
                )
                if self._keyword_retriever is not None
                else ()
            )
        except Exception as exc:
            if isinstance(exc, HybridRetrievalError):
                raise
            raise HybridRetrievalError(
                "Hybrid retrieval failed"
            ) from exc

        merged = self._merge_results(
            semantic_results=semantic_results,
            lexical_results=lexical_results,
        )

        if not merged:
            return ()

        if self._reranker is not None:
            reranked = self._reranker.rerank(
                normalized_query,
                tuple(
                    RetrievalResult(
                        chunk_id=item.chunk_id,
                        text=item.text,
                        score=item.final_score,
                        document_id=item.document_id,
                        source=item.source,
                        metadata=item.metadata,
                    )
                    for item in merged
                ),
            )

            return self._build_reranked_results(reranked)

        merged.sort(
            key=lambda item: (
                -item.final_score,
                item.chunk_id,
            )
        )

        return tuple(merged[: self._top_k])

    def _merge_results(
        self,
        *,
        semantic_results: tuple[RetrievalResult, ...],
        lexical_results: tuple[RetrievalResult, ...],
    ) -> list[HybridRetrievalResult]:
        merged: dict[str, HybridRetrievalResult] = {}

        semantic_max = max(
            (result.score for result in semantic_results),
            default=1.0,
        )

        lexical_max = max(
            (result.score for result in lexical_results),
            default=1.0,
        )

        if semantic_max <= 0:
            semantic_max = 1.0

        if lexical_max <= 0:
            lexical_max = 1.0

        for result in semantic_results:
            normalized_score = result.score / semantic_max

            merged[result.chunk_id] = HybridRetrievalResult(
                chunk_id=result.chunk_id,
                text=result.text,
                semantic_score=result.score,
                rerank_score=0.0,
                final_score=(
                    normalized_score
                    * self._semantic_weight
                ),
                document_id=result.document_id,
                source=result.source,
                metadata=result.metadata,
            )

        for result in lexical_results:
            normalized_score = result.score / lexical_max

            existing = merged.get(result.chunk_id)

            if existing is None:
                merged[result.chunk_id] = HybridRetrievalResult(
                    chunk_id=result.chunk_id,
                    text=result.text,
                    semantic_score=0.0,
                    rerank_score=0.0,
                    final_score=(
                        normalized_score
                        * self._lexical_weight
                    ),
                    document_id=result.document_id,
                    source=result.source,
                    metadata=result.metadata,
                )
                continue

            merged[result.chunk_id] = HybridRetrievalResult(
                chunk_id=existing.chunk_id,
                text=existing.text,
                semantic_score=existing.semantic_score,
                rerank_score=existing.rerank_score,
                final_score=(
                    existing.final_score
                    + normalized_score
                    * self._lexical_weight
                ),
                document_id=existing.document_id,
                source=existing.source,
                metadata=existing.metadata,
            )

        return list(merged.values())

    def _build_reranked_results(
        self,
        results: tuple[RerankedResult, ...],
    ) -> tuple[HybridRetrievalResult, ...]:
        final_results: list[HybridRetrievalResult] = []

        for result in results:
            final_results.append(
                HybridRetrievalResult(
                    chunk_id=result.chunk_id,
                    text=result.text,
                    semantic_score=result.retrieval_score,
                    rerank_score=result.rerank_score,
                    final_score=result.rerank_score,
                    document_id=result.document_id,
                    source=result.source,
                    metadata=result.metadata,
                )
            )

        final_results.sort(
            key=lambda item: (
                -item.final_score,
                item.chunk_id,
            )
        )

        return tuple(final_results[: self._top_k])


__all__ = [
    "HybridRetrievalError",
    "HybridRetrievalResult",
    "HybridRetriever",
    "KeywordRetriever",
    "SimpleKeywordRetriever",
]