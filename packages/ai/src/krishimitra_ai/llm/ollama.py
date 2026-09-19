from __future__ import annotations

from typing import Any

import httpx

from .base import (
    BaseLLMProvider,
    LLMConfigurationError,
    LLMConnectionError,
    LLMRequest,
    LLMResponse,
    LLMResponseError,
    LLMUsage,
)


class OllamaProvider(BaseLLMProvider):
    """Async Ollama provider for local/open LLM inference."""

    name = "ollama"

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.2:3b",
        timeout: float = 120.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        normalized_url = base_url.rstrip("/")

        if not normalized_url:
            raise LLMConfigurationError(
                "Ollama base URL cannot be empty."
            )

        if not default_model.strip():
            raise LLMConfigurationError(
                "Ollama default model cannot be empty."
            )

        if timeout <= 0:
            raise LLMConfigurationError(
                "Ollama timeout must be greater than zero."
            )

        self.base_url = normalized_url
        self.default_model = default_model.strip()
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "OllamaProvider":
        await self._get_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        await self.close()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=False,
            )

        return self._client

    async def close(self) -> None:
        """Close the internally-created HTTP client."""

        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None

    def supports_model(self, model: str) -> bool:
        """Ollama can support locally installed model names."""

        return bool(model.strip())

    async def health_check(self) -> bool:
        """Check whether the Ollama server is reachable."""

        client = await self._get_client()

        try:
            response = await client.get("/api/tags")
            response.raise_for_status()
            return True
        except (httpx.HTTPError, httpx.TimeoutException):
            return False

    async def list_models(self) -> tuple[str, ...]:
        """Return locally available Ollama model names."""

        client = await self._get_client()

        try:
            response = await client.get("/api/tags")
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LLMConnectionError(
                "Timed out while connecting to Ollama."
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMConnectionError(
                f"Unable to connect to Ollama: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise LLMResponseError(
                "Ollama returned invalid JSON while listing models."
            ) from exc

        models = payload.get("models", [])

        if not isinstance(models, list):
            raise LLMResponseError(
                "Ollama model response has an invalid 'models' field."
            )

        names: list[str] = []

        for item in models:
            if not isinstance(item, dict):
                continue

            name = item.get("name")

            if isinstance(name, str) and name.strip():
                names.append(name.strip())

        return tuple(names)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response using Ollama's chat API."""

        model = request.model or self.default_model

        if not model.strip():
            raise LLMConfigurationError(
                "No Ollama model was specified."
            )

        client = await self._get_client()

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in self.build_messages(request)
        ]

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        if request.max_tokens is not None:
            payload["options"]["num_predict"] = request.max_tokens

        try:
            response = await client.post(
                "/api/chat",
                json=payload,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LLMConnectionError(
                "Timed out while waiting for Ollama."
            ) from exc
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            try:
                detail = exc.response.text[:1000]
            except Exception:
                detail = "No response details available."

            raise LLMResponseError(
                f"Ollama returned HTTP {status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMConnectionError(
                f"Unable to communicate with Ollama: {exc}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMResponseError(
                "Ollama returned invalid JSON."
            ) from exc

        return self._parse_response(
            data=data,
            requested_model=model,
        )

    def _parse_response(
        self,
        *,
        data: dict[str, Any],
        requested_model: str,
    ) -> LLMResponse:
        """Convert Ollama's native response into the common response model."""

        if not isinstance(data, dict):
            raise LLMResponseError(
                "Ollama response must be a JSON object."
            )

        message = data.get("message")

        if not isinstance(message, dict):
            raise LLMResponseError(
                "Ollama response is missing the message object."
            )

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise LLMResponseError(
                "Ollama response contains no usable content."
            )

        model = data.get("model", requested_model)

        if not isinstance(model, str) or not model.strip():
            model = requested_model

        usage = self._parse_usage(data)

        return LLMResponse(
            content=content.strip(),
            model=model.strip(),
            provider=self.provider_name,
            finish_reason=self._parse_finish_reason(data),
            usage=usage,
            metadata={
                "done": data.get("done"),
                "done_reason": data.get("done_reason"),
                "total_duration_ns": data.get("total_duration"),
                "load_duration_ns": data.get("load_duration"),
                "prompt_eval_duration_ns": data.get(
                    "prompt_eval_duration"
                ),
                "eval_duration_ns": data.get("eval_duration"),
            },
        )

    @staticmethod
    def _parse_finish_reason(
        data: dict[str, Any],
    ) -> str | None:
        """Extract Ollama's completion reason when available."""

        done_reason = data.get("done_reason")

        if isinstance(done_reason, str) and done_reason.strip():
            return done_reason.strip()

        return None

    @staticmethod
    def _parse_usage(
        data: dict[str, Any],
    ) -> LLMUsage | None:
        """Extract token usage from an Ollama response."""

        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        if not isinstance(prompt_tokens, int):
            prompt_tokens = 0

        if not isinstance(completion_tokens, int):
            completion_tokens = 0

        if prompt_tokens < 0:
            prompt_tokens = 0

        if completion_tokens < 0:
            completion_tokens = 0

        total_tokens = prompt_tokens + completion_tokens

        if total_tokens == 0:
            return None

        return LLMUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )