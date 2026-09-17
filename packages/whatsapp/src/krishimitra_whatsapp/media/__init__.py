"""WhatsApp media handling for KrishiMitra-AI."""

from __future__ import annotations

from krishimitra_whatsapp.media.downloader import (
    DownloadedMedia,
    MediaDownloadClient,
    MediaDownloadError,
    WhatsAppMediaDownloader,
    download_media,
)
from krishimitra_whatsapp.media.metadata import (
    MediaMetadata,
    MediaMetadataExtractor,
    extract_metadata,
)
from krishimitra_whatsapp.media.validator import (
    MediaValidationError,
    MediaValidationResult,
    MediaValidator,
    validate_media,
)

__all__ = [
    "DownloadedMedia",
    "MediaDownloadClient",
    "MediaDownloadError",
    "MediaMetadata",
    "MediaMetadataExtractor",
    "MediaValidationError",
    "MediaValidationResult",
    "MediaValidator",
    "WhatsAppMediaDownloader",
    "download_media",
    "extract_metadata",
    "validate_media",
]