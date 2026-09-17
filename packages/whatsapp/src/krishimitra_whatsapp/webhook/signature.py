"""WhatsApp webhook signature verification for KrishiMitra-AI."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


_SIGNATURE_PREFIX = "sha256="


class SignatureValidationError(ValueError):
    """Raised when a webhook signature is invalid."""


@dataclass(frozen=True, slots=True)
class SignatureValidationResult:
    """Result of webhook signature verification."""

    valid: bool
    reason: str | None = None


class WebhookSignatureVerifier:
    """Verify WhatsApp webhook signatures using HMAC-SHA256."""

    def __init__(self, *, app_secret: str) -> None:
        if not app_secret:
            raise ValueError("app_secret must not be empty")

        if len(app_secret) < 16:
            raise ValueError(
                "app_secret must contain at least 16 characters",
            )

        self._app_secret = app_secret.encode("utf-8")

    def expected_signature(
        self,
        payload: bytes,
    ) -> str:
        """Generate the expected X-Hub-Signature-256 value."""

        if not payload:
            raise ValueError("payload must not be empty")

        digest = hmac.new(
            self._app_secret,
            payload,
            hashlib.sha256,
        ).hexdigest()

        return f"{_SIGNATURE_PREFIX}{digest}"

    def verify(
        self,
        payload: bytes,
        signature: str,
    ) -> SignatureValidationResult:
        """Verify a webhook signature without raising on invalid input."""

        if not payload:
            return SignatureValidationResult(
                valid=False,
                reason="empty_payload",
            )

        if not signature:
            return SignatureValidationResult(
                valid=False,
                reason="missing_signature",
            )

        provided = signature.strip()

        if not provided.startswith(_SIGNATURE_PREFIX):
            return SignatureValidationResult(
                valid=False,
                reason="invalid_signature_format",
            )

        provided_digest = provided[len(_SIGNATURE_PREFIX):]

        if not provided_digest:
            return SignatureValidationResult(
                valid=False,
                reason="empty_signature",
            )

        expected = self.expected_signature(payload)

        if not hmac.compare_digest(
            provided,
            expected,
        ):
            return SignatureValidationResult(
                valid=False,
                reason="signature_mismatch",
            )

        return SignatureValidationResult(valid=True)

    def require_valid(
        self,
        payload: bytes,
        signature: str,
    ) -> None:
        """Verify a signature or raise SignatureValidationError."""

        result = self.verify(
            payload,
            signature,
        )

        if not result.valid:
            raise SignatureValidationError(
                result.reason or "invalid_webhook_signature",
            )


def generate_signature(
    payload: bytes,
    *,
    app_secret: str,
) -> str:
    """Generate a WhatsApp-compatible webhook signature."""

    return WebhookSignatureVerifier(
        app_secret=app_secret,
    ).expected_signature(payload)


def verify_signature(
    payload: bytes,
    signature: str,
    *,
    app_secret: str,
) -> bool:
    """Return whether a webhook signature is valid."""

    return WebhookSignatureVerifier(
        app_secret=app_secret,
    ).verify(
        payload,
        signature,
    ).valid


__all__ = [
    "SignatureValidationError",
    "SignatureValidationResult",
    "WebhookSignatureVerifier",
    "generate_signature",
    "verify_signature",
]