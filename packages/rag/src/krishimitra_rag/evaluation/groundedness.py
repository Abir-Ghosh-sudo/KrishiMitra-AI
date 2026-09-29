from __future__ import annotations

from dataclasses import dataclass


class GroundednessEvaluationError(ValueError):
    """Raised when groundedness evaluation cannot be completed."""


@dataclass(frozen=True, slots=True)
class GroundednessResult:
    """Result of evaluating whether an answer is supported by context."""

    score: float
    grounded: bool
    matched_terms: tuple[str, ...]
    unsupported_terms: tuple[str, ...]


class GroundednessEvaluator:
    """Provides deterministic lexical groundedness evaluation.

    This is an evaluation signal, not a substitute for a trained
    factuality or entailment model.
    """

    def __init__(
        self,
        *,
        minimum_score: float = 0.6,
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
        answer: str,
        contexts: tuple[str, ...] | list[str],
    ) -> GroundednessResult:
        """Evaluate how much of an answer is lexically supported by context."""
        if not isinstance(answer, str):
            raise GroundednessEvaluationError(
                "Answer must be a string"
            )

        normalized_answer = self._normalize(answer)

        if not normalized_answer:
            raise GroundednessEvaluationError(
                "Answer cannot be empty"
            )

        normalized_contexts = tuple(
            self._normalize(context)
            for context in contexts
            if isinstance(context, str) and context.strip()
        )

        if not normalized_contexts:
            return GroundednessResult(
                score=0.0,
                grounded=False,
                matched_terms=(),
                unsupported_terms=(),
            )

        answer_terms = self._extract_terms(normalized_answer)

        if not answer_terms:
            return GroundednessResult(
                score=0.0,
                grounded=False,
                matched_terms=(),
                unsupported_terms=(),
            )

        context_text = " ".join(normalized_contexts)
        context_terms = set(
            self._extract_terms(context_text)
        )

        matched = tuple(
            term
            for term in answer_terms
            if term in context_terms
        )

        unsupported = tuple(
            term
            for term in answer_terms
            if term not in context_terms
        )

        score = len(matched) / len(answer_terms)

        return GroundednessResult(
            score=score,
            grounded=score >= self._minimum_score,
            matched_terms=matched,
            unsupported_terms=unsupported,
        )

    def is_grounded(
        self,
        answer: str,
        contexts: tuple[str, ...] | list[str],
    ) -> bool:
        """Return whether the answer meets the configured groundedness threshold."""
        return self.evaluate(
            answer,
            contexts,
        ).grounded

    def _extract_terms(self, text: str) -> tuple[str, ...]:
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


def evaluate_groundedness(
    answer: str,
    contexts: tuple[str, ...] | list[str],
    *,
    minimum_score: float = 0.6,
) -> GroundednessResult:
    """Convenience wrapper for groundedness evaluation."""
    return GroundednessEvaluator(
        minimum_score=minimum_score,
    ).evaluate(
        answer,
        contexts,
    )


__all__ = [
    "GroundednessEvaluationError",
    "GroundednessEvaluator",
    "GroundednessResult",
    "evaluate_groundedness",
]