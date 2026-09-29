from __future__ import annotations

from dataclasses import dataclass


class RelevanceEvaluationError(ValueError):
    """Raised when retrieval relevance evaluation fails."""


@dataclass(frozen=True, slots=True)
class RelevanceResult:
    """Result of evaluating retrieved context relevance."""

    score: float
    relevant: bool
    matched_terms: tuple[str, ...]
    missing_terms: tuple[str, ...]


class RelevanceEvaluator:
    """Evaluates query-to-context lexical relevance.

    This provides a deterministic evaluation signal. It is intentionally
    independent of any specific embedding or LLM provider.
    """

    def __init__(
        self,
        *,
        minimum_score: float = 0.5,
        minimum_term_length: int = 3,
    ) -> None:
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError(
                "minimum_score must be between 0 and 1"
            )

        if minimum_term_length <= 0:
            raise ValueError(
                "minimum_term_length must be greater than zero"
            )

        self._minimum_score = minimum_score
        self._minimum_term_length = minimum_term_length

    def evaluate(
        self,
        query: str,
        contexts: tuple[str, ...] | list[str],
    ) -> RelevanceResult:
        """Evaluate how relevant retrieved contexts are to a query."""
        if not isinstance(query, str):
            raise RelevanceEvaluationError(
                "Query must be a string"
            )

        normalized_query = self._normalize(query)

        if not normalized_query:
            raise RelevanceEvaluationError(
                "Query cannot be empty"
            )

        normalized_contexts = tuple(
            self._normalize(context)
            for context in contexts
            if isinstance(context, str) and context.strip()
        )

        if not normalized_contexts:
            return RelevanceResult(
                score=0.0,
                relevant=False,
                matched_terms=(),
                missing_terms=self._extract_terms(
                    normalized_query
                ),
            )

        query_terms = self._extract_terms(
            normalized_query
        )

        if not query_terms:
            return RelevanceResult(
                score=0.0,
                relevant=False,
                matched_terms=(),
                missing_terms=(),
            )

        context_text = " ".join(normalized_contexts)

        context_terms = set(
            self._extract_terms(context_text)
        )

        matched_terms = tuple(
            term
            for term in query_terms
            if term in context_terms
        )

        missing_terms = tuple(
            term
            for term in query_terms
            if term not in context_terms
        )

        score = len(matched_terms) / len(query_terms)

        return RelevanceResult(
            score=score,
            relevant=score >= self._minimum_score,
            matched_terms=matched_terms,
            missing_terms=missing_terms,
        )

    def is_relevant(
        self,
        query: str,
        contexts: tuple[str, ...] | list[str],
    ) -> bool:
        """Return whether contexts meet the configured relevance threshold."""
        return self.evaluate(
            query,
            contexts,
        ).relevant

    def _extract_terms(
        self,
        text: str,
    ) -> tuple[str, ...]:
        terms: list[str] = []
        current: list[str] = []

        for character in text:
            if character.isalnum():
                current.append(character)
                continue

            if current:
                term = "".join(current)

                if len(term) >= self._minimum_term_length:
                    terms.append(term)

                current = []

        if current:
            term = "".join(current)

            if len(term) >= self._minimum_term_length:
                terms.append(term)

        return tuple(dict.fromkeys(terms))

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(
            text.lower().strip().split()
        )


def evaluate_relevance(
    query: str,
    contexts: tuple[str, ...] | list[str],
    *,
    minimum_score: float = 0.5,
) -> RelevanceResult:
    """Convenience wrapper for relevance evaluation."""
    return RelevanceEvaluator(
        minimum_score=minimum_score,
    ).evaluate(
        query,
        contexts,
    )


__all__ = [
    "RelevanceEvaluationError",
    "RelevanceEvaluator",
    "RelevanceResult",
    "evaluate_relevance",
]