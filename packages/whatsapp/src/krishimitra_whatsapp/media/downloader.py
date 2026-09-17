"""WhatsApp media download support for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx


class MediaDownloadError(RuntimeError):
    """Raised when WhatsApp media cannot be downloaded."""


@dataclass(frozen=True, slots=True)
class DownloadedMedia:
    """Downloaded WhatsApp media payload."""

    media_id: str
    content: bytes
    content_type: str | None
    filename: str | None
    size_bytes: int


class MediaDownloadClient(Protocol):
    """Protocol for downloading media from a remote URL."""

    async def download(
        self,
        *,
        media_id: str,
        url: str,
        access_token: str,
        filename: str | None = None,
    ) -> DownloadedMedia:
        """Download media and return its contents."""


class WhatsAppMediaDownloader:
    """Download media from the WhatsApp Cloud API media URL."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        max_size_bytes: int = 25 * 1024 * 1024,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero",
            )

        if max_size_bytes <= 0:
            raise ValueError(
                "max_size_bytes must be greater than zero",
            )

        self._timeout = timeout_seconds
        self._max_size_bytes = max_size_bytes
        self._client = client

    async def download(
        self,
        *,
        media_id: str,
        url: str,
        access_token: str,
        filename: str | None = None,
    ) -> DownloadedMedia:
        """Download media from a WhatsApp media URL."""

        normalized_media_id = media_id.strip()
        normalized_url = url.strip()
        normalized_token = access_token.strip()

        if not normalized_media_id:
            raise ValueError("media_id must not be empty")

        if not normalized_url:
            raise ValueError("url must not be empty")

        if not normalized_token:
            raise ValueError("access_token must not be empty")

        headers = {
            "Authorization": f"Bearer {normalized_token}",
        }

        client = self._client
        owns_client = client is None

        if owns_client:
            client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                follow_redirects=False,
            )

        try:
            response = await client.get(
                normalized_url,
                headers=headers,
            )

            if response.status_code >= 400:
                raise MediaDownloadError(
                    f"media download failed with HTTP "
                    f"{response.status_code}",
                )

            content_length = response.headers.get(
                "content-length",
            )

            if content_length is not None:
                try:
                    declared_size = int(content_length)
                except ValueError:
                    declared_size = None

                if (
                    declared_size is not None
                    and declared_size > self._max_size_bytes
                ):
                    raise MediaDownloadError(
                        "media exceeds the configured size limit",
                    )

            content = response.content

            if len(content) > self._max_size_bytes:
                raise MediaDownloadError(
                    "downloaded media exceeds the configured size limit",
                )

            content_type = response.headers.get(
                "content-type",
            )

            return DownloadedMedia(
                media_id=normalized_media_id,
                content=content,
                content_type=content_type,
                filename=filename,
                size_bytes=len(content),
            )

        except httpx.HTTPError as exc:
            raise MediaDownloadError(
                f"media download request failed: {exc}",
            ) from exc

        finally:
            if owns_client:
                await client.aclose()


async def download_media(
    *,
    media_id: str,
    url: str,
    access_token: str,
    filename: str | None = None,
    timeout_seconds: float = 30.0,
    max_size_bytes: int = 25 * 1024 * 1024,
) -> DownloadedMedia:
    """Download WhatsApp media using the default downloader."""

    downloader = WhatsAppMediaDownloader(
        timeout_seconds=timeout_seconds,
        max_size_bytes=max_size_bytes,
    )

    return await downloader.download(
        media_id=media_id,
        url=url,
        access_token=access_token,
        filename=filename,
    )


__all__ = [
    "DownloadedMedia",
    "MediaDownloadClient",
    "MediaDownloadError",
    "WhatsAppMediaDownloader",
    "download_media",
]