from __future__ import annotations

from dataclasses import dataclass


class RAGChunkingError(ValueError):
    """Raised when RAG document chunking fails."""


@dataclass(frozen=True, slots=True)
class RAGChunk:
    """A chunk produced during RAG knowledge ingestion."""

    chunk_id: int
    text: str
    start_character: int
    end_character: int


class RAGChunker:
    """Creates deterministic overlapping chunks for RAG ingestion."""

    def __init__(
        self,
        *,
        chunk_size: int = 1000,
        overlap: int = 150,
        min_chunk_size: int = 100,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        if min_chunk_size <= 0:
            raise ValueError("min_chunk_size must be greater than zero")

        if min_chunk_size > chunk_size:
            raise ValueError("min_chunk_size cannot exceed chunk_size")

        self._chunk_size = chunk_size
        self._overlap = overlap
        self._min_chunk_size = min_chunk_size

    def chunk(self, text: str) -> tuple[RAGChunk, ...]:
        """Split cleaned text into deterministic overlapping chunks."""
        if not isinstance(text, str):
            raise RAGChunkingError("Text must be a string")

        normalized = text.strip()

        if not normalized:
            raise RAGChunkingError("Text cannot be empty")

        chunks: list[RAGChunk] = []
        start = 0
        chunk_id = 0
        text_length = len(normalized)

        while start < text_length:
            proposed_end = min(
                start + self._chunk_size,
                text_length,
            )

            end = self._find_boundary(
                normalized,
                start=start,
                proposed_end=proposed_end,
            )

            chunk_text = normalized[start:end].strip()

            if chunk_text:
                chunks.append(
                    RAGChunk(
                        chunk_id=chunk_id,
                        text=chunk_text,
                        start_character=start,
                        end_character=end,
                    )
                )
                chunk_id += 1

            if end >= text_length:
                break

            next_start = max(0, end - self._overlap)

            if next_start <= start:
                next_start = end

            start = next_start

        return tuple(chunks)

    def _find_boundary(
        self,
        text: str,
        *,
        start: int,
        proposed_end: int,
    ) -> int:
        if proposed_end >= len(text):
            return len(text)

        minimum_boundary = min(
            proposed_end,
            start + self._min_chunk_size,
        )

        newline = text.rfind("\n", minimum_boundary, proposed_end)

        if newline > start:
            return newline

        sentence_candidates = (
            text.rfind(". ", minimum_boundary, proposed_end),
            text.rfind("? ", minimum_boundary, proposed_end),
            text.rfind("! ", minimum_boundary, proposed_end),
        )

        sentence_boundary = max(sentence_candidates)

        if sentence_boundary > start:
            return sentence_boundary + 1

        whitespace = text.rfind(" ", minimum_boundary, proposed_end)

        if whitespace > start:
            return whitespace

        return proposed_end


def chunk_text(
    text: str,
    *,
    chunk_size: int = 1000,
    overlap: int = 150,
    min_chunk_size: int = 100,
) -> tuple[RAGChunk, ...]:
    """Convenience wrapper for RAG chunking."""
    return RAGChunker(
        chunk_size=chunk_size,
        overlap=overlap,
        min_chunk_size=min_chunk_size,
    ).chunk(text)


__all__ = [
    "RAGChunk",
    "RAGChunker",
    "RAGChunkingError",
    "chunk_text",
]