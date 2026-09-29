"""Document processing services for KrishiMitra-AI."""

from .chunker import (
    DocumentChunk,
    DocumentChunker,
    DocumentChunkingError,
    chunk_document,
)
from .extractor import (
    DocumentExtractionError,
    DocumentExtractor,
    DocumentExtractorBackend,
    ExtractedDocument,
)
from .ocr import (
    OCRBackend,
    OCRProcessingError,
    OCRProcessor,
    OCRResult,
    has_usable_ocr_text,
)
from .parser import (
    DocumentFormat,
    DocumentParseError,
    DocumentParser,
    DocumentParserBackend,
    ParsedDocument,
)
from .pdf import (
    PDFBackend,
    PDFPage,
    PDFProcessingError,
    PDFProcessor,
    ParsedPDF,
    is_pdf,
)
from .validators import (
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    DEFAULT_MAX_FILE_SIZE_BYTES,
    DocumentValidationError,
    DocumentValidationResult,
    DocumentValidator,
    validate_document,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "ALLOWED_DOCUMENT_EXTENSIONS",
    "ALLOWED_MIME_TYPES",
    "DEFAULT_MAX_FILE_SIZE_BYTES",
    "DocumentChunk",
    "DocumentChunker",
    "DocumentChunkingError",
    "DocumentExtractionError",
    "DocumentExtractor",
    "DocumentExtractorBackend",
    "DocumentFormat",
    "DocumentParseError",
    "DocumentParser",
    "DocumentParserBackend",
    "DocumentValidationError",
    "DocumentValidationResult",
    "DocumentValidator",
    "ExtractedDocument",
    "OCRBackend",
    "OCRProcessingError",
    "OCRProcessor",
    "OCRResult",
    "PDFBackend",
    "PDFPage",
    "PDFProcessingError",
    "PDFProcessor",
    "ParsedDocument",
    "ParsedPDF",
    "chunk_document",
    "has_usable_ocr_text",
    "is_pdf",
    "validate_document",
]