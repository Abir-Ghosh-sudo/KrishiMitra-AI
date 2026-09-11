"""RAG and knowledge retrieval models for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeSourceType(StrEnum):
    """Types of agricultural knowledge sources."""

    GOVERNMENT = "government"
    AGRICULTURAL_RESEARCH = "agricultural_research"
    EXTENSION = "extension"
    DOCUMENT = "document"
    EXPERT = "expert"
    OTHER = "other"


class RetrievalResult(BaseModel):
    """A retrieved knowledge item used to ground an AI response."""

    model_config = ConfigDict(extra="forbid")

    result_id: UUID

    source_type: KnowledgeSourceType

    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)

    source_name: str | None = Field(default=None, max_length=300)
    source_url: str | None = None

    relevance_score: float = Field(ge=0.0, le=1.0)

    document_id: UUID | None = None
    chunk_id: UUID | None = None

    metadata: dict[str, str] = Field(default_factory=dict)


class RAGContext(BaseModel):
    """Grounded context assembled for an AI response."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)

    results: list[RetrievalResult] = Field(default_factory=list)

    context_text: str = ""

    grounded: bool = False

    confidence: float = Field(ge=0.0, le=1.0)

    limitations: list[str] = Field(default_factory=list)


__all__ = [
    "KnowledgeSourceType",
    "RAGContext",
    "RetrievalResult",
]