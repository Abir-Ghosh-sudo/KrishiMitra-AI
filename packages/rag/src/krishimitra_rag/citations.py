from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class CitationError(ValueError):
    """Raised when citation data is invalid."""


@dataclass(frozen=True, slots=True)
class Citation:
    """A grounded reference attached to retrieved knowledge."""

    citation_id: str
    title: str
    source: str
    chunk_id: int | None = None
    document_id: str | None = None
    url: str | None = None
    excerpt: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()


class CitationBuilder:
    """Build and normalize citations from retrieval results."""

    def build(
        self,
        *,
        citation_id: str,
        title: str,
        source: str,
        chunk_id: int | None = None,
        document_id: str | None = None,
        url: str | None = None,
        excerpt: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Citation:
        if not citation_id.strip():
            raise CitationError("Citation ID cannot be empty")

        if not title.strip():
            raise CitationError("Citation title cannot be empty")

        if not source.strip():
            raise CitationError("Citation source cannot be empty")

        if chunk_id is not None and chunk_id < 0:
            raise CitationError("Chunk ID cannot be negative")

        normalized_metadata = tuple(
            sorted(
                (
                    str(key).strip(),
                    str(value).strip(),
                )
                for key, value in (metadata or {}).items()
                if str(key).strip()
            )
        )

        return Citation(
            citation_id=citation_id.strip(),
            title=title.strip(),
            source=source.strip(),
            chunk_id=chunk_id,
            document_id=document_id.strip()
            if document_id
            else None,
            url=url.strip() if url else None,
            excerpt=excerpt.strip() if excerpt else None,
            metadata=normalized_metadata,
        )

    def from_retrieval_result(
        self,
        result: object,
        *,
        citation_id: str,
        title: str | None = None,
    ) -> Citation:
        """Create a citation from a compatible retrieval result."""
        source = getattr(result, "source", None)
        text = getattr(result, "text", None)
        chunk_id = getattr(result, "chunk_id", None)
        document_id = getattr(result, "document_id", None)
        metadata = getattr(result, "metadata", ())

        if not source:
            raise CitationError(
                "Retrieval result does not contain a source"
            )

        if isinstance(metadata, tuple):
            metadata_dict = dict(metadata)
        elif isinstance(metadata, dict):
            metadata_dict = metadata
        else:
            metadata_dict = {}

        resolved_title = (
            title
            or metadata_dict.get("title")
            or source
        )

        return self.build(
            citation_id=citation_id,
            title=resolved_title,
            source=source,
            chunk_id=chunk_id,
            document_id=str(document_id)
            if document_id is not None
            else None,
            url=metadata_dict.get("url"),
            excerpt=text,
            metadata=metadata_dict,
        )


def deduplicate_citations(
    citations: Iterable[Citation],
) -> tuple[Citation, ...]:
    """Remove duplicate citations while preserving first-seen order."""
    unique: list[Citation] = []
    seen: set[tuple[str, str, int | None]] = set()

    for citation in citations:
        key = (
            citation.source,
            citation.document_id or citation.citation_id,
            citation.chunk_id,
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(citation)

    return tuple(unique)


def format_citation(citation: Citation) -> str:
    """Format one citation for a grounded response."""
    parts = [citation.title, citation.source]

    if citation.chunk_id is not None:
        parts.append(f"chunk {citation.chunk_id}")

    return " — ".join(parts)


def format_citations(
    citations: Iterable[Citation],
) -> tuple[str, ...]:
    """Format multiple citations deterministically."""
    return tuple(
        format_citation(citation)
        for citation in citations
    )


__all__ = [
    "Citation",
    "CitationBuilder",
    "CitationError",
    "deduplicate_citations",
    "format_citation",
    "format_citations",
]