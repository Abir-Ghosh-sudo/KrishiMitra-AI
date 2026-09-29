"""Evaluation utilities for KrishiMitra-AI RAG."""

from .groundedness import (
    GroundednessEvaluationError,
    GroundednessEvaluator,
    GroundednessResult,
    evaluate_groundedness,
)
from .relevance import (
    RelevanceEvaluationError,
    RelevanceEvaluator,
    RelevanceResult,
    evaluate_relevance,
)
from .retrieval import (
    RetrievalEvaluationError,
    RetrievalEvaluationResult,
    RetrievalEvaluator,
    hit_rate_at_k,
    precision_at_k,
    recall_at_k,
)

__all__ = [
    "GroundednessEvaluationError",
    "GroundednessEvaluator",
    "GroundednessResult",
    "RelevanceEvaluationError",
    "RelevanceEvaluator",
    "RelevanceResult",
    "RetrievalEvaluationError",
    "RetrievalEvaluationResult",
    "RetrievalEvaluator",
    "evaluate_groundedness",
    "evaluate_relevance",
    "hit_rate_at_k",
    "precision_at_k",
    "recall_at_k",
]