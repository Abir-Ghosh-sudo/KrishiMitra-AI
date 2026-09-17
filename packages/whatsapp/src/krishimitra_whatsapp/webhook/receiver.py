"""WhatsApp webhook receiving orchestration for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from krishimitra_whatsapp.webhook.parser import (
    ParsedWebhook,
    WebhookPayloadParser,
)
from krishimitra_whatsapp.webhook.signature import (
    SignatureValidationError,
    WebhookSignatureVerifier,
)


@dataclass(frozen=True, slots=True)
class WebhookReceiveResult:
    """Result of receiving and validating a WhatsApp webhook."""

    accepted: bool
    parsed: ParsedWebhook | None = None
    reason: str | None = None


class WhatsAppWebhookReceiver:
    """Receive, authenticate, and parse WhatsApp webhook payloads.

    The receiver deliberately stops after validation and parsing. Heavy
    processing such as AI inference, vision, speech, RAG, or recommendations
    must happen in the worker layer.
    """

    def __init__(
        self,
        *,
        app_secret: str,
        parser: WebhookPayloadParser | None = None,
    ) -> None:
        self._signature_verifier = WebhookSignatureVerifier(
            app_secret=app_secret,
        )
        self._parser = parser or WebhookPayloadParser()

    def receive(
        self,
        payload: bytes,
        signature: str,
        parsed_payload: dict[str, Any],
    ) -> WebhookReceiveResult:
        """Validate the raw payload and parse the decoded webhook body."""

        try:
            self._signature_verifier.require_valid(
                payload,
                signature,
            )
        except SignatureValidationError as exc:
            return WebhookReceiveResult(
                accepted=False,
                reason=str(exc),
            )

        try:
            parsed = self._parser.parse(
                parsed_payload,
            )
        except (TypeError, ValueError) as exc:
            return WebhookReceiveResult(
                accepted=False,
                reason=f"invalid_payload: {exc}",
            )

        return WebhookReceiveResult(
            accepted=True,
            parsed=parsed,
        )

    def require_receive(
        self,
        payload: bytes,
        signature: str,
        parsed_payload: dict[str, Any],
    ) -> ParsedWebhook:
        """Receive a webhook or raise an error."""

        result = self.receive(
            payload,
            signature,
            parsed_payload,
        )

        if not result.accepted or result.parsed is None:
            raise ValueError(
                result.reason or "webhook_rejected",
            )

        return result.parsed


__all__ = [
    "WebhookReceiveResult",
    "WhatsAppWebhookReceiver",
]