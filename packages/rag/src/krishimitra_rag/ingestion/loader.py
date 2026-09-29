from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class KnowledgeLoadError(RuntimeError):
    """Raised when a knowledge source cannot be loaded."""


@dataclass(frozen=True, slots=True)
class LoadedDocument:
    """Raw document content loaded from a knowledge source."""

    source: str
    filename: str
    content: bytes


class KnowledgeLoaderBackend(Protocol):
    """Backend contract for loading external or local knowledge."""

    def load(self, source: str) -> LoadedDocument:
        """Load a document from a source."""


class KnowledgeLoader:
    """Loads knowledge through an injected backend."""

    def __init__(self, backend: KnowledgeLoaderBackend) -> None:
        self._backend = backend

    def load(self, source: str) -> LoadedDocument:
        if not isinstance(source, str):
            raise KnowledgeLoadError("Source must be a string")

        normalized_source = source.strip()

        if not normalized_source:
            raise KnowledgeLoadError("Source cannot be empty")

        try:
            document = self._backend.load(normalized_source)
        except KnowledgeLoadError:
            raise
        except Exception as exc:
            raise KnowledgeLoadError(
                f"Failed to load knowledge source: {normalized_source}"
            ) from exc

        if not isinstance(document, LoadedDocument):
            raise KnowledgeLoadError(
                "Loader backend returned an invalid LoadedDocument"
            )

        if not document.content:
            raise KnowledgeLoadError(
                f"Knowledge source is empty: {normalized_source}"
            )

        filename = self._normalize_filename(document.filename)

        return LoadedDocument(
            source=document.source.strip() or normalized_source,
            filename=filename,
            content=bytes(document.content),
        )

    @staticmethod
    def _normalize_filename(filename: str) -> str:
        if not isinstance(filename, str):
            raise KnowledgeLoadError("Filename must be a string")

        normalized = filename.strip()

        if not normalized:
            raise KnowledgeLoadError("Filename cannot be empty")

        if "\x00" in normalized:
            raise KnowledgeLoadError(
                "Filename contains an invalid null byte"
            )

        return Path(normalized).name


class LocalFileLoader:
    """Simple local-file backend for controlled knowledge ingestion."""

    def load(self, source: str) -> LoadedDocument:
        path = Path(source)

        if not path.exists():
            raise KnowledgeLoadError(
                f"Knowledge file does not exist: {source}"
            )

        if not path.is_file():
            raise KnowledgeLoadError(
                f"Knowledge source is not a file: {source}"
            )

        try:
            content = path.read_bytes()
        except OSError as exc:
            raise KnowledgeLoadError(
                f"Unable to read knowledge file: {source}"
            ) from exc

        if not content:
            raise KnowledgeLoadError(
                f"Knowledge file is empty: {source}"
            )

        return LoadedDocument(
            source=str(path),
            filename=path.name,
            content=content,
        )


def load_local_file(source: str) -> LoadedDocument:
    """Load a local knowledge file."""
    return KnowledgeLoader(LocalFileLoader()).load(source)


__all__ = [
    "KnowledgeLoadError",
    "KnowledgeLoader",
    "KnowledgeLoaderBackend",
    "LoadedDocument",
    "LocalFileLoader",
    "load_local_file",
]