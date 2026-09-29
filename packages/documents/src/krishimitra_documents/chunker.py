from __future__ import annotations

from dataclasses import dataclass


class DocumentChunkingError(ValueError):
    """Raised when document chunking fails."""


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    """A single chunk prepared for downstream RAG processing."""

    chunk_id: int
    text: str
    start_character: int
    end_character: int


class DocumentChunker:
    """Splits normalized document text into deterministic overlapping chunks."""

    def __init__(
        self,
        *,
        chunk_size: int = 1000,
        overlap: int = 150,
        min_chunk_size: int = 50,
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

    def chunk(self, text: str) -> tuple[DocumentChunk, ...]:
        """Split text into deterministic overlapping chunks."""
        if not isinstance(text, str):
            raise DocumentChunkingError("Document text must be a string")

        normalized_text = self._normalize_text(text)

        if not normalized_text:
            raise DocumentChunkingError("Document text cannot be empty")

        chunks: list[DocumentChunk] = []
        start = 0
        chunk_id = 0
        text_length = len(normalized_text)

        while start < text_length:
            proposed_end = min(
                start + self._chunk_size,
                text_length,
            )

            end = self._find_boundary(
                normalized_text,
                start=start,
                proposed_end=proposed_end,
            )

            chunk_text = normalized_text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
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

        return self._merge_small_final_chunk(tuple(chunks))

    def _find_boundary(
        self,
        text: str,
        *,
        start: int,
        proposed_end: int,
    ) -> int:
        if proposed_end >= len(text):
            return len(text)

        boundary_start = min(
            proposed_end,
            start + self._min_chunk_size,
        )

        newline_boundary = text.rfind("\n", boundary_start, proposed_end)
        if newline_boundary > start:
            return newline_boundary

        sentence_boundaries = (
            text.rfind(". ", boundary_start, proposed_end),
            text.rfind("? ", boundary_start, proposed_end),
            text.rfind("! ", boundary_start, proposed_end),
        )

        sentence_boundary = max(sentence_boundaries)

        if sentence_boundary > start:
            return sentence_boundary + 1

        whitespace_boundary = text.rfind(" ", boundary_start, proposed_end)

        if whitespace_boundary > start:
            return whitespace_boundary

        return proposed_end

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = (
            line.strip()
            for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        )

        return "\n".join(
            line
            for line in lines
            if line
        ).strip()

    @staticmethod
    def _merge_small_final_chunk(
        chunks: tuple[DocumentChunk, ...],
    ) -> tuple[DocumentChunk, ...]:
        if len(chunks) < 2:
            return chunks

        previous = chunks[-2]
        final = chunks[-1]

        if len(final.text) >= 50:
            return chunks

        merged_text = f"{previous.text} {final.text}".strip()

        merged_chunk = DocumentChunk(
            chunk_id=previous.chunk_id,
            text=merged_text,
            start_character=previous.start_character,
            end_character=final.end_character,
        )

        return (*chunks[:-2], merged_chunk)


def chunk_document(
    text: str,
    *,
    chunk_size: int = 1000,
    overlap: int = 150,
    min_chunk_size: int = 50,
) -> tuple[DocumentChunk, ...]:
    """Convenience wrapper around DocumentChunker."""
    return DocumentChunker(
        chunk_size=chunk_size,
        overlap=overlap,
        min_chunk_size=min_chunk_size,
    ).chunk(text)


__all__ = [
    "DocumentChunk",
    "DocumentChunker",
    "DocumentChunkingError",
    "chunk_document",
]