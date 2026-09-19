from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping

from .context_builder import AIContext, ContextBuilder
from .intent_router import IntentResult, IntentRouter
from .response_generator import (
    GeneratedResponse,
    ResponseGenerationRequest,
    ResponseGenerator,
)
from .tool_router import ToolName, ToolPlan, ToolRequest, ToolRouter


ToolHandler = Callable[
    [ToolRequest],
    Awaitable[Any],
]


@dataclass(frozen=True, slots=True)
class OrchestrationRequest:
    """Input received by the AI orchestration layer."""

    user_message: str
    context: AIContext | None = None
    language: str | None = None
    request_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    """Result produced by one domain tool."""

    tool: ToolName
    success: bool
    data: Any = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    """Complete result returned by the AI orchestrator."""

    intent: IntentResult
    tool_plan: ToolPlan
    tool_results: tuple[ToolExecutionResult, ...]
    response: GeneratedResponse | None
    requires_clarification: bool = False
    clarification_message: str | None = None


class OrchestrationError(RuntimeError):
    """Raised when the orchestration pipeline cannot continue."""


class AIOrchestrator:
    """
    Coordinate intent routing, context preparation, tool execution,
    and final response generation.

    Heavy domain logic stays outside this class.
    """

    def __init__(
        self,
        *,
        intent_router: IntentRouter,
        tool_router: ToolRouter,
        response_generator: ResponseGenerator,
        tool_handlers: Mapping[ToolName, ToolHandler] | None = None,
    ) -> None:
        self._intent_router = intent_router
        self._tool_router = tool_router
        self._response_generator = response_generator
        self._tool_handlers = dict(tool_handlers or {})

    def register_tool(
        self,
        tool: ToolName,
        handler: ToolHandler,
    ) -> None:
        """Register or replace a domain-tool handler."""

        if not callable(handler):
            raise TypeError("Tool handler must be callable.")

        self._tool_handlers[tool] = handler

    def unregister_tool(self, tool: ToolName) -> None:
        """Remove a registered tool handler."""

        self._tool_handlers.pop(tool, None)

    async def process(
        self,
        request: OrchestrationRequest,
    ) -> OrchestrationResult:
        """Run the complete AI orchestration pipeline."""

        user_message = request.user_message.strip()

        if not user_message:
            raise OrchestrationError(
                "Cannot orchestrate an empty user message."
            )

        # ---------------------------------------------------------
        # 1. Intent detection
        # ---------------------------------------------------------
        intent_result = self._route_intent(user_message)

        # ---------------------------------------------------------
        # 2. Build context
        # ---------------------------------------------------------
        context = request.context or self._build_context(request)

        # ---------------------------------------------------------
        # 3. Build tool execution plan
        # ---------------------------------------------------------
        tool_context = self._build_tool_context(
            request=request,
            context=context,
        )

        tool_plan = self._tool_router.build_plan(
            intent_result,
            context=tool_context,
        )

        # ---------------------------------------------------------
        # 4. Clarification path
        # ---------------------------------------------------------
        if tool_plan.requires_clarification:
            return OrchestrationResult(
                intent=intent_result,
                tool_plan=tool_plan,
                tool_results=(),
                response=None,
                requires_clarification=True,
                clarification_message=(
                    tool_plan.clarification_reason
                    or "Please provide a little more information."
                ),
            )

        # ---------------------------------------------------------
        # 5. Execute domain tools
        # ---------------------------------------------------------
        tool_results = await self._execute_tools(tool_plan)

        # ---------------------------------------------------------
        # 6. Generate final farmer-facing response
        # ---------------------------------------------------------
        response_request = ResponseGenerationRequest(
            user_message=user_message,
            context=context,
            tool_results=self._results_as_mapping(tool_results),
            language=request.language,
            request_id=request.request_id,
        )

        response = await self._response_generator.generate(
            response_request
        )

        return OrchestrationResult(
            intent=intent_result,
            tool_plan=tool_plan,
            tool_results=tool_results,
            response=response,
        )

    def _route_intent(
        self,
        user_message: str,
    ) -> IntentResult:
        """Run deterministic first-stage intent routing."""

        try:
            return self._intent_router.route(user_message)
        except Exception as exc:
            raise OrchestrationError(
                "Intent routing failed."
            ) from exc

    @staticmethod
    def _build_context(
        request: OrchestrationRequest,
    ) -> AIContext:
        """
        Build a minimal context when no pre-built context was supplied.

        External services should enrich this context before orchestration
        whenever farm/weather/history data is available.
        """

        builder = ContextBuilder()

        if request.language:
            builder.add_additional(
                "preferred_language",
                request.language,
            )

        if request.request_id:
            builder.add_additional(
                "request_id",
                request.request_id,
            )

        if request.metadata:
            builder.add_additional(
                "request_metadata",
                dict(request.metadata),
            )

        return builder.build()

    @staticmethod
    def _build_tool_context(
        *,
        request: OrchestrationRequest,
        context: AIContext,
    ) -> dict[str, Any]:
        """Convert orchestration context into controlled tool parameters."""

        result: dict[str, Any] = {
            "language": request.language,
            "request_id": request.request_id,
        }

        context_data = context.model_dump(
            mode="json",
            exclude_none=True,
        )

        for key, value in context_data.items():
            if isinstance(value, Mapping):
                result.update(value)
            else:
                result[key] = value

        result.update(request.metadata)

        return result

    async def _execute_tools(
        self,
        tool_plan: ToolPlan,
    ) -> tuple[ToolExecutionResult, ...]:
        """Execute planned tools while isolating individual failures."""

        results: list[ToolExecutionResult] = []

        for tool_request in tool_plan.tools:
            handler = self._tool_handlers.get(tool_request.name)

            if handler is None:
                if tool_request.mode.value == "required":
                    results.append(
                        ToolExecutionResult(
                            tool=tool_request.name,
                            success=False,
                            error=(
                                f"No handler registered for "
                                f"{tool_request.name.value}."
                            ),
                        )
                    )
                continue

            try:
                data = await handler(tool_request)

                results.append(
                    ToolExecutionResult(
                        tool=tool_request.name,
                        success=True,
                        data=data,
                    )
                )

            except Exception as exc:
                results.append(
                    ToolExecutionResult(
                        tool=tool_request.name,
                        success=False,
                        error=self._safe_error_message(exc),
                    )
                )

                # A required tool failure is recorded but does not expose
                # the internal exception to the farmer-facing layer.
                if tool_request.mode.value == "required":
                    break

        return tuple(results)

    @staticmethod
    def _results_as_mapping(
        results: tuple[ToolExecutionResult, ...],
    ) -> dict[str, Any]:
        """Convert tool results into response-generator input."""

        output: dict[str, Any] = {}

        for result in results:
            if result.success:
                output[result.tool.value] = {
                    "success": True,
                    "data": result.data,
                }
            else:
                output[result.tool.value] = {
                    "success": False,
                    "error": result.error,
                }

        return output

    @staticmethod
    def _safe_error_message(exc: Exception) -> str:
        """
        Return a safe operational error.

        Provider credentials, stack traces, database URLs and internal
        implementation details must never reach the farmer.
        """

        message = str(exc).strip()

        if not message:
            return "Tool execution failed."

        sensitive_markers = (
            "password=",
            "secret=",
            "api_key=",
            "token=",
            "authorization=",
            "postgresql://",
            "redis://",
        )

        lowered = message.lower()

        if any(marker in lowered for marker in sensitive_markers):
            return "Tool execution failed."

        return message[:500]