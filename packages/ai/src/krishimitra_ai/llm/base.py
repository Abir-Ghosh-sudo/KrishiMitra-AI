from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class LLMMessage:
    """A single message exchanged with an LLM."""

    role: str
    content: str

    def __post_init__(self) -> None:
        role = self.role.strip().lower()
        content = self.content.strip()

        if not role:
            raise ValueError("LLM message role cannot be empty.")

        if not content:
            raise ValueError("LLM message content cannot be empty.")

        object.__setattr__(self, "role", role)
        object.__setattr__(self, "content", content)


@dataclass(frozen=True, slots=True)
class LLMRequest:
    """Provider-independent request sent to an LLM."""

    messages: tuple[LLMMessage, ...]
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    system_prompt: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.messages:
            raise ValueError("LLM request must contain at least one message.")

        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0.")

        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")

        if self.model is not None and not self.model.strip():
            raise ValueError("model cannot be blank.")

        if self.system_prompt is not None and not self.system_prompt.strip():
            raise ValueError("system_prompt cannot be blank.")

        object.__setattr__(
            self,
            "messages",
            tuple(self.messages),
        )


@dataclass(frozen=True, slots=True)
class LLMUsage:
    """Token and request usage returned by an LLM provider."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __post_init__(self) -> None:
        if self.prompt_tokens < 0:
            raise ValueError("prompt_tokens cannot be negative.")

        if self.completion_tokens < 0:
            raise ValueError("completion_tokens cannot be negative.")

        if self.total_tokens < 0:
            raise ValueError("total_tokens cannot be negative.")


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """Provider-independent response returned by an LLM."""

    content: str
    model: str
    provider: str
    finish_reason: str | None = None
    usage: LLMUsage | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("LLM response content cannot be empty.")

        if not self.model.strip():
            raise ValueError("LLM response model cannot be empty.")

        if not self.provider.strip():
            raise ValueError("LLM response provider cannot be empty.")


class LLMError(RuntimeError):
    """Base exception for LLM provider failures."""


class LLMConfigurationError(LLMError):
    """Raised when an LLM provider is incorrectly configured."""


class LLMConnectionError(LLMError):
    """Raised when an LLM provider cannot be reached."""


class LLMResponseError(LLMError):
    """Raised when an LLM provider returns an invalid response."""


class BaseLLMProvider(ABC):
    """Provider-independent interface for language models."""

    name: str

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the provider."""

    async def health_check(self) -> bool:
        """Return whether the provider is currently reachable."""

        return True

    def supports_model(self, model: str) -> bool:
        """Return whether this provider supports the requested model."""

        return bool(model.strip())

    @property
    def provider_name(self) -> str:
        """Stable provider identifier used by orchestration and observability."""

        return self.name

    def build_messages(
        self,
        request: LLMRequest,
    ) -> tuple[LLMMessage, ...]:
        """Build the final provider-independent message sequence."""

        if request.system_prompt is None:
            return request.messages

        return (
            LLMMessage(
                role="system",
                content=request.system_prompt,
            ),
            *request.messages,
        )


def normalize_messages(
    messages: Sequence[LLMMessage],
) -> tuple[LLMMessage, ...]:
    """Normalize an arbitrary message sequence into an immutable tuple."""

    normalized = tuple(messages)

    if not normalized:
        raise ValueError("At least one LLM message is required.")

    return normalized