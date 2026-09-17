"""WhatsApp webhook endpoint verification for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
import hmac


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """Result of a webhook verification request."""

    verified: bool
    challenge: str | None = None
    reason: str | None = None


class WebhookVerificationError(ValueError):
    """Raised when webhook verification fails."""


class WebhookVerifier:
    """Verify Meta WhatsApp webhook subscription requests."""

    def __init__(self, *, verify_token: str) -> None:
        if not verify_token:
            raise ValueError("verify_token must not be empty")

        self._verify_token = verify_token

    def verify(
        self,
        *,
        mode: str | None,
        token: str | None,
        challenge: str | None,
    ) -> VerificationResult:
        """Validate verification parameters."""

        if mode != "subscribe":
            return VerificationResult(
                verified=False,
                reason="invalid_mode",
            )

        if token is None or not token:
            return VerificationResult(
                verified=False,
                reason="missing_verify_token",
            )

        if not hmac.compare_digest(
            token,
            self._verify_token,
        ):
            return VerificationResult(
                verified=False,
                reason="verify_token_mismatch",
            )

        if challenge is None or not challenge:
            return VerificationResult(
                verified=False,
                reason="missing_challenge",
            )

        return VerificationResult(
            verified=True,
            challenge=challenge,
        )

    def require_valid(
        self,
        *,
        mode: str | None,
        token: str | None,
        challenge: str | None,
    ) -> str:
        """Verify a request and return its challenge."""

        result = self.verify(
            mode=mode,
            token=token,
            challenge=challenge,
        )

        if not result.verified or result.challenge is None:
            raise WebhookVerificationError(
                result.reason or "webhook_verification_failed",
            )

        return result.challenge


def verify_webhook(
    *,
    mode: str | None,
    token: str | None,
    challenge: str | None,
    verify_token: str,
) -> VerificationResult:
    """Convenience function for webhook verification."""

    return WebhookVerifier(
        verify_token=verify_token,
    ).verify(
        mode=mode,
        token=token,
        challenge=challenge,
    )


__all__ = [
    "VerificationResult",
    "WebhookVerificationError",
    "WebhookVerifier",
    "verify_webhook",
]