from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .base import BaseLLMProvider, LLMConfigurationError, LLMRequest, LLMResponse


@dataclass(frozen=True, slots=True)
class ModelRoute:
    """Describes which provider should handle a model."""

    provider: BaseLLMProvider
    models: frozenset[str]

    def supports(self, model: str) -> bool:
        """Return whether this route supports the requested model."""

        normalized = model.strip().lower()

        if not normalized:
            return False

        if normalized in self.models:
            return True

        return self.provider.supports_model(model)


class ModelRouter:
    """
    Routes LLM requests to an appropriate provider.

    The router deliberately contains no provider-specific inference logic.
    Providers are injected at application startup, which keeps the AI layer
    testable and allows Ollama or another local/open provider to be swapped
    without changing the orchestrator.
    """

    def __init__(
        self,
        providers: Iterable[BaseLLMProvider],
        *,
        default_provider: str | None = None,
        default_model: str | None = None,
    ) -> None:
        provider_list = tuple(providers)

        if not provider_list:
            raise LLMConfigurationError(
                "At least one LLM provider must be configured."
            )

        self._providers = {
            provider.provider_name.strip().lower(): provider
            for provider in provider_list
        }

        if len(self._providers) != len(provider_list):
            raise LLMConfigurationError(
                "Duplicate LLM provider names are not allowed."
            )

        self._default_provider = (
            default_provider.strip().lower()
            if default_provider is not None
            else None
        )

        self._default_model = (
            default_model.strip()
            if default_model is not None
            else None
        )

        if self._default_provider is not None:
            if self._default_provider not in self._providers:
                raise LLMConfigurationError(
                    f"Unknown default LLM provider: {default_provider}"
                )

        if self._default_model is not None and not self._default_model:
            raise LLMConfigurationError(
                "Default model cannot be blank."
            )

    @property
    def providers(self) -> tuple[BaseLLMProvider, ...]:
        """Return configured providers."""

        return tuple(self._providers.values())

    @property
    def default_provider(self) -> str | None:
        """Return the configured default provider."""

        return self._default_provider

    @property
    def default_model(self) -> str | None:
        """Return the configured default model."""

        return self._default_model

    def get_provider(self, name: str) -> BaseLLMProvider:
        """Resolve a provider by its stable name."""

        normalized = name.strip().lower()

        if not normalized:
            raise LLMConfigurationError(
                "Provider name cannot be blank."
            )

        try:
            return self._providers[normalized]
        except KeyError as exc:
            raise LLMConfigurationError(
                f"Unknown LLM provider: {name}"
            ) from exc

    def find_provider_for_model(
        self,
        model: str,
    ) -> BaseLLMProvider | None:
        """Find the first provider capable of handling a model."""

        normalized = model.strip()

        if not normalized:
            return None

        for provider in self._providers.values():
            if provider.supports_model(normalized):
                return provider

        return None

    def resolve(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> BaseLLMProvider:
        """
        Resolve a provider using the following priority:

        1. Explicit provider.
        2. Provider capable of the explicit model.
        3. Configured default provider.
        4. Provider capable of the configured default model.
        5. The only configured provider.
        """

        if provider is not None:
            resolved_provider = self.get_provider(provider)

            if model is not None and not resolved_provider.supports_model(
                model
            ):
                raise LLMConfigurationError(
                    f"Provider '{provider}' does not support model '{model}'."
                )

            return resolved_provider

        if model is not None:
            resolved_provider = self.find_provider_for_model(model)

            if resolved_provider is not None:
                return resolved_provider

            raise LLMConfigurationError(
                f"No configured LLM provider supports model '{model}'."
            )

        if self._default_provider is not None:
            return self._providers[self._default_provider]

        if self._default_model is not None:
            resolved_provider = self.find_provider_for_model(
                self._default_model
            )

            if resolved_provider is not None:
                return resolved_provider

        if len(self._providers) == 1:
            return next(iter(self._providers.values()))

        raise LLMConfigurationError(
            "Unable to resolve an LLM provider. "
            "Configure a default provider or specify one explicitly."
        )

    async def generate(
        self,
        request: LLMRequest,
        *,
        provider: str | None = None,
    ) -> LLMResponse:
        """Route a request and execute generation."""

        requested_model = request.model or self._default_model

        resolved_provider = self.resolve(
            provider=provider,
            model=requested_model,
        )

        return await resolved_provider.generate(request)

    async def health_check(self) -> dict[str, bool]:
        """Run health checks for all configured providers."""

        results: dict[str, bool] = {}

        for name, provider in self._providers.items():
            try:
                results[name] = await provider.health_check()
            except Exception:
                results[name] = False

        return results