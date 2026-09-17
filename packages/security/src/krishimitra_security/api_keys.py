"""API key generation and verification for KrishiMitra-AI."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


_API_KEY_PREFIX = "km_"
_DEFAULT_KEY_BYTES = 32


def _hash_key(api_key: str) -> str:
    """Create a deterministic SHA-256 hash for an API key."""

    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    """Return the current UTC timestamp."""

    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class ApiKey:
    """Metadata for a generated API key.

    The raw secret is deliberately not stored in this object.
    """

    key_id: UUID
    key_hash: str
    name: str
    created_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    @property
    def is_revoked(self) -> bool:
        """Return whether the key has been revoked."""

        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        """Return whether the key has passed its expiration time."""

        if self.expires_at is None:
            return False

        return _utc_now() >= self.expires_at

    @property
    def is_active(self) -> bool:
        """Return whether the key can currently be used."""

        return not self.is_revoked and not self.is_expired


@dataclass(frozen=True, slots=True)
class GeneratedApiKey:
    """Result returned when a new API key is generated."""

    key: ApiKey

    raw_key: str


class ApiKeyManager:
    """Generate, register, revoke, and verify API keys.

    This class provides an application-level abstraction. Production
    persistence should store ``ApiKey.key_hash`` and metadata in the
    database, never ``GeneratedApiKey.raw_key``.
    """

    def __init__(self) -> None:
        self._keys: dict[UUID, ApiKey] = {}

    def generate(
        self,
        name: str,
        *,
        expires_at: datetime | None = None,
        key_bytes: int = _DEFAULT_KEY_BYTES,
    ) -> GeneratedApiKey:
        """Generate and register a cryptographically secure API key."""

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("API key name must not be empty")

        if len(normalized_name) > 200:
            raise ValueError("API key name must not exceed 200 characters")

        if key_bytes < 32:
            raise ValueError("key_bytes must be at least 32")

        if expires_at is not None:
            if expires_at.tzinfo is None:
                raise ValueError("expires_at must be timezone-aware")

            if expires_at <= _utc_now():
                raise ValueError("expires_at must be in the future")

        raw_key = (
            f"{_API_KEY_PREFIX}"
            f"{secrets.token_urlsafe(key_bytes)}"
        )

        key = ApiKey(
            key_id=uuid4(),
            key_hash=_hash_key(raw_key),
            name=normalized_name,
            created_at=_utc_now(),
            expires_at=expires_at,
        )

        self._keys[key.key_id] = key

        return GeneratedApiKey(
            key=key,
            raw_key=raw_key,
        )

    def verify(
        self,
        raw_key: str,
    ) -> ApiKey | None:
        """Verify a raw API key and return its metadata when valid."""

        if not raw_key:
            return None

        key_hash = _hash_key(raw_key)

        for key in self._keys.values():
            if not hmac.compare_digest(key.key_hash, key_hash):
                continue

            if not key.is_active:
                return None

            return key

        return None

    def revoke(
        self,
        key_id: UUID,
    ) -> bool:
        """Revoke an API key."""

        key = self._keys.get(key_id)

        if key is None or key.is_revoked:
            return False

        self._keys[key_id] = ApiKey(
            key_id=key.key_id,
            key_hash=key.key_hash,
            name=key.name,
            created_at=key.created_at,
            expires_at=key.expires_at,
            revoked_at=_utc_now(),
        )

        return True

    def get(
        self,
        key_id: UUID,
    ) -> ApiKey | None:
        """Return API key metadata without exposing its secret."""

        return self._keys.get(key_id)

    def count(self) -> int:
        """Return the number of registered API keys."""

        return len(self._keys)


__all__ = [
    "ApiKey",
    "ApiKeyManager",
    "GeneratedApiKey",
]