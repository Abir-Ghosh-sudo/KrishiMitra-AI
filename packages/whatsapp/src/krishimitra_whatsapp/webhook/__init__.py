"""WhatsApp webhook integration for KrishiMitra-AI."""

from __future__ import annotations

from krishimitra_whatsapp.webhook.parser import (
    ParsedMessage,
    ParsedMessageType,
    ParsedWebhook,
    WebhookPayloadParser,
    parse_webhook,
)
from krishimitra_whatsapp.webhook.receiver import (
    WhatsAppWebhookReceiver,
    WebhookReceiveResult,
)
from krishimitra_whatsapp.webhook.signature import (
    SignatureValidationError,
    SignatureValidationResult,
    WebhookSignatureVerifier,
    generate_signature,
    verify_signature,
)
from krishimitra_whatsapp.webhook.verification import (
    VerificationResult,
    WebhookVerificationError,
    WebhookVerifier,
    verify_webhook,
)

__all__ = [
    "ParsedMessage",
    "ParsedMessageType",
    "ParsedWebhook",
    "SignatureValidationError",
    "SignatureValidationResult",
    "VerificationResult",
    "WebhookPayloadParser",
    "WebhookReceiveResult",
    "WebhookSignatureVerifier",
    "WebhookVerificationError",
    "WebhookVerifier",
    "WhatsAppWebhookReceiver",
    "generate_signature",
    "parse_webhook",
    "verify_signature",
    "verify_webhook",
]