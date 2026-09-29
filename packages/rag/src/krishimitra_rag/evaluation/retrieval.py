from __future__ import annotations

from dataclasses import dataclass


class RetrievalEvaluationError(ValueError):
    """Raised when retrieval quality evaluation fails."""


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationResult:
    """Evaluation metrics for a retrieved result set."""

    precision_at_k: float
    recall_at_k: float
    hit_rate: float
    retrieved_count: int
    relevant_retrieved_count: int
    expected_relevant_count: int


class RetrievalEvaluator:
    """Evaluates retrieval quality against known relevant chunk IDs."""

    def __init__(self, *, k: int = 5) -> None:
        if k <= 0:
            raise ValueError(
                "k must be greater than zero"
            )

        self._k = k

    def evaluate(
        self,
        retrieved_ids: tuple[str, ...] | list[str],
        relevant_ids: tuple[str, ...] | set[str] | list[str],
    ) -> RetrievalEvaluationResult:
        """Calculate Precision@K, Recall@K, and Hit Rate."""
        retrieved = self._normalize_ids(
            retrieved_ids,
            field_name="retrieved_ids",
        )

        relevant = set(
            self._normalize_ids(
                relevant_ids,
                field_name="relevant_ids",
            )
        )

        top_k = retrieved[: self._k]

        retrieved_set = set(top_k)

        relevant_retrieved_count = len(
            retrieved_set & relevant
        )

        retrieved_count = len(top_k)
        expected_relevant_count = len(relevant)

        precision_at_k = (
            relevant_retrieved_count / retrieved_count
            if retrieved_count
            else 0.0
        )

        recall_at_k = (
            relevant_retrieved_count / expected_relevant_count
            if expected_relevant_count
            else 0.0
        )

        hit_rate = (
            1.0
            if relevant_retrieved_count > 0
            else 0.0
        )

        return RetrievalEvaluationResult(
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            hit_rate=hit_rate,
            retrieved_count=retrieved_count,
            relevant_retrieved_count=relevant_retrieved_count,
            expected_relevant_count=expected_relevant_count,
        )

    def evaluate_batch(
        self,
        queries: list[
            tuple[
                tuple[str, ...] | list[str],
                tuple[str, ...] | set[str] | list[str],
            ]
        ],
    ) -> tuple[RetrievalEvaluationResult, ...]:
        """Evaluate multiple retrieval queries."""
        results: list[RetrievalEvaluationResult] = []

        for retrieved_ids, relevant_ids in queries:
            results.append(
                self.evaluate(
                    retrieved_ids,
                    relevant_ids,
                )
            )

        return tuple(results)

    @staticmethod
    def _normalize_ids(
        ids: tuple[str, ...]
        | list[str]
        | set[str],
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        if not isinstance(ids, (tuple, list, set)):
            raise RetrievalEvaluationError(
                f"{field_name} must be a tuple, list, or set"
            )

        normalized: list[str] = []

        for item in ids:
            if not isinstance(item, str):
                raise RetrievalEvaluationError(
                    f"{field_name} must contain strings only"
                )

            value = item.strip()

            if not value:
                raise RetrievalEvaluationError(
                    f"{field_name} cannot contain empty IDs"
                )

            normalized.append(value)

        # Preserve retrieval order while removing duplicates.
        return tuple(dict.fromkeys(normalized))


def precision_at_k(
    retrieved_ids: tuple[str, ...] | list[str],
    relevant_ids: tuple[str, ...] | set[str] | list[str],
    *,
    k: int = 5,
) -> float:
    """Calculate Precision@K."""
    return RetrievalEvaluator(k=k).evaluate(
        retrieved_ids,
        relevant_ids,
    ).precision_at_k


def recall_at_k(
    retrieved_ids: tuple[str, ...] | list[str],
    relevant_ids: tuple[str, ...] | set[str] | list[str],
    *,
    k: int = 5,
) -> float:
    """Calculate Recall@K."""
    return RetrievalEvaluator(k=k).evaluate(
        retrieved_ids,
        relevant_ids,
    ).recall_at_k


def hit_rate_at_k(
    retrieved_ids: tuple[str, ...] | list[str],
    relevant_ids: tuple[str, ...] | set[str] | list[str],
    *,
    k: int = 5,
) -> float:
    """Calculate Hit Rate@K."""
    return RetrievalEvaluator(k=k).evaluate(
        retrieved_ids,
        relevant_ids,
    ).hit_rate


__all__ = [
    "RetrievalEvaluationError",
    "RetrievalEvaluationResult",
    "RetrievalEvaluator",
    "hit_rate_at_k",
    "precision_at_k",
    "recall_at_k",
]