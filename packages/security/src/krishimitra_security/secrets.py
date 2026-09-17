"""Secret management primitives for KrishiMitra-AI."""

from __future__ import annotations

import hmac
import secrets as secrets_module
from dataclasses import dataclass
from hashlib import sha256
from threading import RLock


@dataclass(frozen=True, slots=True)
class SecretMetadata:
    """Metadata describing a managed secret without exposing its value."""

    name: str
    version: int
    fingerprint: str


class SecretManager:
    """In-memory secret manager abstraction.

    The application layer can replace this implementation with a production
    secret backend such as environment variables, Docker/Kubernetes secrets,
    or a dedicated secret-management service.
    """

    def __init__(self) -> None:
        self._secrets: dict[str, dict[int, str]] = {}
        self._current_versions: dict[str, int] = {}
        self._lock = RLock()

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip()

        if not normalized:
            raise ValueError("secret name must not be empty")

        if len(normalized) > 200:
            raise ValueError(
                "secret name must not exceed 200 characters",
            )

        return normalized

    @staticmethod
    def _fingerprint(value: str) -> str:
        return sha256(
            value.encode("utf-8"),
        ).hexdigest()

    def set(
        self,
        name: str,
        value: str,
        *,
        version: int | None = None,
    ) -> SecretMetadata:
        """Store a secret and return non-sensitive metadata."""

        normalized_name = self._normalize_name(name)

        if not value:
            raise ValueError("secret value must not be empty")

        with self._lock:
            versions = self._secrets.setdefault(
                normalized_name,
                {},
            )

            if version is None:
                current_version = self._current_versions.get(
                    normalized_name,
                    0,
                )
                version = current_version + 1

            if version < 1:
                raise ValueError("version must be greater than zero")

            versions[version] = value
            self._current_versions[normalized_name] = version

        return SecretMetadata(
            name=normalized_name,
            version=version,
            fingerprint=self._fingerprint(value),
        )

    def get(
        self,
        name: str,
        *,
        version: int | None = None,
    ) -> str | None:
        """Retrieve a secret by name and optional version."""

        normalized_name = self._normalize_name(name)

        with self._lock:
            versions = self._secrets.get(normalized_name)

            if versions is None:
                return None

            if version is None:
                version = self._current_versions.get(
                    normalized_name,
                )

            if version is None:
                return None

            return versions.get(version)

    def require(
        self,
        name: str,
        *,
        version: int | None = None,
    ) -> str:
        """Retrieve a secret or raise an error."""

        value = self.get(
            name,
            version=version,
        )

        if value is None:
            raise KeyError(
                f"secret not found: {name}",
            )

        return value

    def has(
        self,
        name: str,
        *,
        version: int | None = None,
    ) -> bool:
        """Return whether a secret version exists."""

        return self.get(
            name,
            version=version,
        ) is not None

    def metadata(
        self,
        name: str,
        *,
        version: int | None = None,
    ) -> SecretMetadata | None:
        """Return metadata without exposing the secret value."""

        value = self.get(
            name,
            version=version,
        )

        if value is None:
            return None

        normalized_name = self._normalize_name(name)

        with self._lock:
            resolved_version = version

            if resolved_version is None:
                resolved_version = self._current_versions.get(
                    normalized_name,
                )

        if resolved_version is None:
            return None

        return SecretMetadata(
            name=normalized_name,
            version=resolved_version,
            fingerprint=self._fingerprint(value),
        )

    def delete(
        self,
        name: str,
        *,
        version: int | None = None,
    ) -> bool:
        """Delete a specific secret version or the current version."""

        normalized_name = self._normalize_name(name)

        with self._lock:
            versions = self._secrets.get(normalized_name)

            if not versions:
                return False

            resolved_version = version

            if resolved_version is None:
                resolved_version = self._current_versions.get(
                    normalized_name,
                )

            if resolved_version is None:
                return False

            removed = versions.pop(resolved_version, None)

            if removed is None:
                return False

            if not versions:
                self._secrets.pop(normalized_name, None)
                self._current_versions.pop(normalized_name, None)
                return True

            if self._current_versions.get(normalized_name) == resolved_version:
                self._current_versions[normalized_name] = max(versions)

            return True

    def rotate(
        self,
        name: str,
        *,
        length: int = 48,
    ) -> SecretMetadata:
        """Generate and store a cryptographically secure replacement secret."""

        if length < 32:
            raise ValueError("secret length must be at least 32")

        value = secrets_module.token_urlsafe(length)

        return self.set(
            name,
            value,
        )

    def verify(
        self,
        name: str,
        candidate: str,
        *,
        version: int | None = None,
    ) -> bool:
        """Constant-time comparison of a candidate secret."""

        if not candidate:
            return False

        stored = self.get(
            name,
            version=version,
        )

        if stored is None:
            return False

        return hmac.compare_digest(
            stored,
            candidate,
        )

    def clear(self) -> None:
        """Remove all managed secrets."""

        with self._lock:
            self._secrets.clear()
            self._current_versions.clear()


__all__ = [
    "SecretManager",
    "SecretMetadata",
]