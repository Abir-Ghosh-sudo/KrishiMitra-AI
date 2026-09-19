from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..llm.base import LLMMessage, LLMRequest
from ..llm.model_router import ModelRouter
from ..llm.prompts import (
    RESPONSE_FORMAT_INSTRUCTION,
    build_system_prompt,
    build_user_prompt,
)
from .context_builder import AIContext


@dataclass(frozen=True, slots=True)
class ResponseGenerationRequest:
    """Input required to generate a farmer-facing response."""

    user_message: str
    context: AIContext | None = None
    tool_results: Mapping[str, Any] = field(default_factory=dict)
    language: str | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class GeneratedResponse:
    """Final response generated for the farmer."""

    text: str
    model: str
    provider: str
    request_id: str | None = None
    usage: Mapping[str, int] = field(default_factory=dict)


class ResponseGenerationError(RuntimeError):
    """Raised when response generation fails."""


class ResponseGenerator:
    """
    Generate concise, grounded, safety-aware farmer-facing responses.

    The generator is intentionally independent of a specific LLM provider.
    ModelRouter decides which configured provider/model performs generation.
    """

    def __init__(
        self,
        model_router: ModelRouter,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> None:
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0.")

        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")

        self._model_router = model_router
        self._temperature = temperature
        self._max_tokens = max_tokens

    async def generate(
        self,
        request: ResponseGenerationRequest,
    ) -> GeneratedResponse:
        """Generate a final farmer-facing response."""

        user_message = request.user_message.strip()

        if not user_message:
            raise ResponseGenerationError(
                "Cannot generate a response for an empty user message."
            )

        context_data = self._build_context_data(request)

        system_prompt = build_system_prompt(
            language=request.language,
        )

        user_prompt = build_user_prompt(
            request.user_message,
            context=context_data,
        )

        messages = (
            LLMMessage(
                role="system",
                content=system_prompt,
            ),
            LLMMessage(
                role="user",
                content=(
                    f"{user_prompt}\n\n"
                    f"{RESPONSE_FORMAT_INSTRUCTION}"
                ),
            ),
        )

        llm_request = LLMRequest(
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )

        try:
            response = await self._model_router.generate(llm_request)
        except Exception as exc:
            raise ResponseGenerationError(
                "Failed to generate the farmer-facing response."
            ) from exc

        text = self._sanitize_response(response.content)

        if not text:
            raise ResponseGenerationError(
                "The language model returned an empty response."
            )

        usage = self._extract_usage(response)

        return GeneratedResponse(
            text=text,
            model=response.model,
            provider=response.provider,
            request_id=request.request_id,
            usage=usage,
        )

    @staticmethod
    def _build_context_data(
        request: ResponseGenerationRequest,
    ) -> dict[str, Any]:
        """Build a controlled context payload for the LLM."""

        data: dict[str, Any] = {}

        if request.context is not None:
            data["farm_context"] = request.context.model_dump(
                mode="json",
                exclude_none=True,
            )

        if request.tool_results:
            data["tool_results"] = ResponseGenerator._sanitize_tool_results(
                request.tool_results
            )

        if request.language:
            data["preferred_language"] = request.language

        return data

    @staticmethod
    def _sanitize_tool_results(
        tool_results: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Keep tool output structured while removing obviously unsafe
        implementation-level fields before passing data to the LLM.
        """

        blocked_keys = {
            "password",
            "secret",
            "api_key",
            "access_token",
            "refresh_token",
            "authorization",
            "private_key",
        }

        def clean(value: Any) -> Any:
            if isinstance(value, Mapping):
                return {
                    str(key): clean(item)
                    for key, item in value.items()
                    if str(key).lower() not in blocked_keys
                }

            if isinstance(value, (list, tuple)):
                return [clean(item) for item in value]

            if isinstance(value, set):
                return [clean(item) for item in value]

            if hasattr(value, "model_dump"):
                return clean(
                    value.model_dump(
                        mode="json",
                        exclude_none=True,
                    )
                )

            if hasattr(value, "__dict__"):
                return clean(vars(value))

            return value

        return clean(tool_results)

    @staticmethod
    def _sanitize_response(text: str) -> str:
        """
        Normalize model output without changing its agricultural meaning.
        """

        cleaned = text.strip()

        if not cleaned:
            return ""

        # Prevent accidental prompt/control markers from becoming part
        # of the farmer-facing response.
        dangerous_prefixes = (
            "system:",
            "developer:",
            "assistant:",
        )

        lines = cleaned.splitlines()
        filtered_lines: list[str] = []

        for line in lines:
            if line.strip().lower() in dangerous_prefixes:
                continue

            filtered_lines.append(line.rstrip())

        return "\n".join(filtered_lines).strip()

    @staticmethod
    def _extract_usage(response: Any) -> dict[str, int]:
        """Extract provider usage metrics when available."""

        usage = getattr(response, "usage", None)

        if usage is None:
            return {}

        if hasattr(usage, "model_dump"):
            raw = usage.model_dump()
        elif isinstance(usage, Mapping):
            raw = dict(usage)
        else:
            raw = {}

        result: dict[str, int] = {}

        for key in (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
        ):
            value = raw.get(key)

            if isinstance(value, int):
                result[key] = value

        return result