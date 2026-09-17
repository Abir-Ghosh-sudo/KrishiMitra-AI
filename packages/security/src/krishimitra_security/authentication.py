"""Authentication primitives for KrishiMitra-AI."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class AuthenticationMethod(StrEnum):
    """Supported authentication mechanisms."""

    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    INTERNAL_SERVICE = "internal_service"


class AuthenticationError(ValueError):
    """Raised when authentication fails."""


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Identity established after successful authentication."""

    principal_id: UUID
    subject: str
    method: AuthenticationMethod
    authenticated_at: datetime
    expires_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        """Return whether the authenticated session has expired."""

        if self.expires_at is None:
            return False

        return datetime.now(timezone.utc) >= self.expires_at


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    """Result of an authentication attempt."""

    authenticated: bool
    principal: AuthenticatedPrincipal | None = None
    reason: str | None = None


class AuthenticationService:
    """Authenticate trusted application principals.

    The service intentionally does not persist credentials. Credential
    storage and identity-provider integration belong to the application
    or infrastructure layer.
    """

    def __init__(
        self,
        *,
        token_secret: str,
        token_ttl: timedelta | None = None,
    ) -> None:
        if not token_secret:
            raise ValueError("token_secret must not be empty")

        if len(token_secret) < 32:
            raise ValueError("token_secret must contain at least 32 characters")

        if token_ttl is not None and token_ttl <= timedelta(0):
            raise ValueError("token_ttl must be greater than zero")

        self._token_secret = token_secret.encode("utf-8")
        self._token_ttl = token_ttl

    def issue_internal_token(
        self,
        subject: str,
    ) -> str:
        """Issue a signed short-lived internal authentication token."""

        normalized_subject = subject.strip()

        if not normalized_subject:
            raise ValueError("subject must not be empty")

        if len(normalized_subject) > 200:
            raise ValueError("subject must not exceed 200 characters")

        issued_at = int(datetime.now(timezone.utc).timestamp())

        payload = f"{normalized_subject}:{issued_at}"
        signature = hmac.new(
            self._token_secret,
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return f"{payload}:{signature}"

    def authenticate_token(
        self,
        token: str,
        *,
        method: AuthenticationMethod = AuthenticationMethod.BEARER_TOKEN,
    ) -> AuthenticationResult:
        """Authenticate a token created by this service."""

        if not token:
            return AuthenticationResult(
                authenticated=False,
                reason="missing_token",
            )

        parts = token.split(":", maxsplit=2)

        if len(parts) != 3:
            return AuthenticationResult(
                authenticated=False,
                reason="malformed_token",
            )

        subject, timestamp_text, provided_signature = parts

        if not subject or not timestamp_text or not provided_signature:
            return AuthenticationResult(
                authenticated=False,
                reason="malformed_token",
            )

        try:
            issued_timestamp = int(timestamp_text)
        except ValueError:
            return AuthenticationResult(
                authenticated=False,
                reason="invalid_timestamp",
            )

        payload = f"{subject}:{issued_timestamp}"

        expected_signature = hmac.new(
            self._token_secret,
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            provided_signature,
            expected_signature,
        ):
            return AuthenticationResult(
                authenticated=False,
                reason="invalid_signature",
            )

        authenticated_at = datetime.fromtimestamp(
            issued_timestamp,
            tz=timezone.utc,
        )

        expires_at = (
            authenticated_at + self._token_ttl
            if self._token_ttl is not None
            else None
        )

        principal = AuthenticatedPrincipal(
            principal_id=uuid4(),
            subject=subject,
            method=method,
            authenticated_at=authenticated_at,
            expires_at=expires_at,
        )

        if principal.is_expired:
            return AuthenticationResult(
                authenticated=False,
                reason="expired_token",
            )

        return AuthenticationResult(
            authenticated=True,
            principal=principal,
        )

    def require_authentication(
        self,
        token: str,
        *,
        method: AuthenticationMethod = AuthenticationMethod.BEARER_TOKEN,
    ) -> AuthenticatedPrincipal:
        """Authenticate a token or raise AuthenticationError."""

        result = self.authenticate_token(
            token,
            method=method,
        )

        if not result.authenticated or result.principal is None:
            raise AuthenticationError(
                result.reason or "authentication_failed",
            )

        return result.principal


__all__ = [
    "AuthenticatedPrincipal",
    "AuthenticationError",
    "AuthenticationMethod",
    "AuthenticationResult",
    "AuthenticationService",
]