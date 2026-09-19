from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterable, Mapping

from .intent_router import IntentResult, IntentType


class ToolName(StrEnum):
    """Domain tools available to the AI orchestrator."""

    WEATHER = "weather"
    VISION = "vision"
    PEST = "pest"
    DISEASE = "disease"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    SOIL = "soil"
    CROP_RECOMMENDATION = "crop_recommendation"
    CROP_STAGE = "crop_stage"
    YIELD_PREDICTION = "yield_prediction"
    SUSTAINABILITY = "sustainability"
    ENERGY = "energy"
    RAG = "rag"
    DOCUMENT = "document"
    FARM = "farm"
    SIMULATION = "simulation"
    MARKET = "market"
    ALERTS = "alerts"
    EXPERT = "expert"


class ToolExecutionMode(StrEnum):
    """Execution mode for a selected tool."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    FALLBACK = "fallback"


@dataclass(frozen=True, slots=True)
class ToolRequest:
    """One tool selected for an AI request."""

    name: ToolName
    mode: ToolExecutionMode
    reason: str
    parameters: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        reason = self.reason.strip()

        if not reason:
            raise ValueError("Tool request reason cannot be empty.")

        object.__setattr__(self, "reason", reason)


@dataclass(frozen=True, slots=True)
class ToolPlan:
    """Complete tool execution plan for one AI request."""

    intent: IntentType
    confidence: float
    tools: tuple[ToolRequest, ...]
    requires_clarification: bool = False
    clarification_reason: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Tool plan confidence must be between 0.0 and 1.0."
            )

        if (
            self.requires_clarification
            and not self.clarification_reason
        ):
            raise ValueError(
                "Clarification reason is required when clarification is needed."
            )


class ToolRouter:
    """
    Convert intent-routing results into executable domain-tool plans.

    This class contains orchestration policy only. Actual implementations
    live in their respective packages.
    """

    _INTENT_TO_TOOLS: dict[
        IntentType,
        tuple[ToolName, ...],
    ] = {
        IntentType.GENERAL_ADVISORY: (
            ToolName.RAG,
        ),
        IntentType.DISEASE_DIAGNOSIS: (
            ToolName.VISION,
            ToolName.DISEASE,
            ToolName.WEATHER,
            ToolName.RAG,
        ),
        IntentType.PEST_IDENTIFICATION: (
            ToolName.VISION,
            ToolName.PEST,
            ToolName.WEATHER,
            ToolName.RAG,
        ),
        IntentType.WEATHER: (
            ToolName.WEATHER,
        ),
        IntentType.IRRIGATION: (
            ToolName.WEATHER,
            ToolName.IRRIGATION,
            ToolName.FARM,
        ),
        IntentType.FERTILIZER: (
            ToolName.SOIL,
            ToolName.FERTILIZER,
            ToolName.WEATHER,
            ToolName.RAG,
        ),
        IntentType.SOIL_ANALYSIS: (
            ToolName.SOIL,
            ToolName.DOCUMENT,
            ToolName.RAG,
        ),
        IntentType.CROP_RECOMMENDATION: (
            ToolName.FARM,
            ToolName.WEATHER,
            ToolName.SOIL,
            ToolName.CROP_RECOMMENDATION,
            ToolName.RAG,
        ),
        IntentType.CROP_STAGE: (
            ToolName.CROP_STAGE,
            ToolName.WEATHER,
            ToolName.FARM,
            ToolName.RAG,
        ),
        IntentType.YIELD_PREDICTION: (
            ToolName.FARM,
            ToolName.CROP_STAGE,
            ToolName.WEATHER,
            ToolName.YIELD_PREDICTION,
        ),
        IntentType.SUSTAINABILITY: (
            ToolName.FARM,
            ToolName.WATER if hasattr(ToolName, "WATER") else ToolName.IRRIGATION,
            ToolName.ENERGY,
            ToolName.SUSTAINABILITY,
        ),
        IntentType.ENERGY_OPTIMIZATION: (
            ToolName.FARM,
            ToolName.WEATHER,
            ToolName.IRRIGATION,
            ToolName.ENERGY,
        ),
        IntentType.MARKET: (
            ToolName.MARKET,
        ),
        IntentType.DOCUMENT_ANALYSIS: (
            ToolName.DOCUMENT,
            ToolName.RAG,
        ),
        IntentType.FARM_STATUS: (
            ToolName.FARM,
            ToolName.WEATHER,
        ),
        IntentType.SIMULATION: (
            ToolName.FARM,
            ToolName.SIMULATION,
            ToolName.RAG,
        ),
        IntentType.ALERTS: (
            ToolName.ALERTS,
            ToolName.WEATHER,
            ToolName.FARM,
        ),
        IntentType.EXPERT_ESCALATION: (
            ToolName.EXPERT,
        ),
    }

    _DEFAULT_REASONS: dict[ToolName, str] = {
        ToolName.WEATHER:
            "Current or forecast weather may affect the recommendation.",
        ToolName.VISION:
            "Visual evidence may be required for image-based analysis.",
        ToolName.DISEASE:
            "Disease analysis is required by the detected intent.",
        ToolName.PEST:
            "Pest analysis is required by the detected intent.",
        ToolName.IRRIGATION:
            "Water requirement or irrigation planning is involved.",
        ToolName.FERTILIZER:
            "Nutrient or fertilizer planning is involved.",
        ToolName.SOIL:
            "Soil information can materially affect the recommendation.",
        ToolName.CROP_RECOMMENDATION:
            "Crop suitability needs to be evaluated.",
        ToolName.CROP_STAGE:
            "Crop growth stage affects the requested decision.",
        ToolName.YIELD_PREDICTION:
            "Yield estimation requires the prediction service.",
        ToolName.SUSTAINABILITY:
            "Sustainability metrics are relevant to the request.",
        ToolName.ENERGY:
            "Energy/resource optimization is relevant.",
        ToolName.RAG:
            "Grounded agricultural knowledge may be required.",
        ToolName.DOCUMENT:
            "Document content may be required for the request.",
        ToolName.FARM:
            "Farm-specific context is relevant.",
        ToolName.SIMULATION:
            "A what-if scenario requires the simulation engine.",
        ToolName.MARKET:
            "Market information is relevant to the request.",
        ToolName.ALERTS:
            "Alert configuration or evaluation is relevant.",
        ToolName.EXPERT:
            "Human agricultural expert review is requested or required.",
    }

    def __init__(
        self,
        *,
        enabled_tools: Iterable[ToolName] | None = None,
    ) -> None:
        if enabled_tools is None:
            self._enabled_tools = frozenset(ToolName)
        else:
            self._enabled_tools = frozenset(enabled_tools)

    @property
    def enabled_tools(self) -> frozenset[ToolName]:
        """Return currently enabled tools."""

        return self._enabled_tools

    def build_plan(
        self,
        intent_result: IntentResult,
        *,
        context: Mapping[str, object] | None = None,
    ) -> ToolPlan:
        """Build a tool plan from an intent result."""

        if intent_result.requires_clarification:
            return ToolPlan(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                tools=(),
                requires_clarification=True,
                clarification_reason=(
                    intent_result.clarification_reason
                    or "Additional information is required."
                ),
            )

        tool_names = self._INTENT_TO_TOOLS.get(
            intent_result.intent,
            (ToolName.RAG,),
        )

        tools = self._build_requests(
            tool_names,
            context=context or {},
        )

        if not tools:
            return ToolPlan(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                tools=(),
                requires_clarification=True,
                clarification_reason=(
                    "No enabled domain tool can handle this request."
                ),
            )

        return ToolPlan(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            tools=tools,
        )

    def _build_requests(
        self,
        tool_names: Iterable[ToolName],
        *,
        context: Mapping[str, object],
    ) -> tuple[ToolRequest, ...]:
        """Convert tool names into executable requests."""

        requests: list[ToolRequest] = []

        for index, tool_name in enumerate(tool_names):
            if tool_name not in self._enabled_tools:
                continue

            mode = (
                ToolExecutionMode.REQUIRED
                if index == 0
                else ToolExecutionMode.OPTIONAL
            )

            parameters = self._parameters_for(
                tool_name,
                context,
            )

            requests.append(
                ToolRequest(
                    name=tool_name,
                    mode=mode,
                    reason=self._DEFAULT_REASONS.get(
                        tool_name,
                        "The tool is relevant to the detected intent.",
                    ),
                    parameters=parameters,
                )
            )

        return tuple(requests)

    @staticmethod
    def _parameters_for(
        tool_name: ToolName,
        context: Mapping[str, object],
    ) -> dict[str, object]:
        """
        Select only context relevant to a tool.

        This prevents unrelated farmer information from being forwarded
        blindly to every downstream service.
        """

        common_keys = {
            "farmer_id",
            "farm_id",
            "crop_id",
            "crop",
            "crop_stage",
            "location",
            "language",
            "request_id",
        }

        tool_specific_keys: dict[ToolName, set[str]] = {
            ToolName.WEATHER: {
                "latitude",
                "longitude",
                "location",
                "forecast_days",
            },
            ToolName.VISION: {
                "image_id",
                "media_id",
                "image",
            },
            ToolName.DISEASE: {
                "disease_candidates",
                "severity",
                "diagnosis",
            },
            ToolName.PEST: {
                "pest_candidates",
                "severity",
                "diagnosis",
            },
            ToolName.IRRIGATION: {
                "soil_moisture",
                "water_requirement",
                "irrigation_history",
                "rainfall",
            },
            ToolName.FERTILIZER: {
                "soil_ph",
                "soil_npk",
                "soil_report",
                "nutrient_status",
            },
            ToolName.SOIL: {
                "soil_report",
                "soil_test",
                "soil_ph",
                "soil_npk",
            },
            ToolName.YIELD_PREDICTION: {
                "historical_yield",
                "weather_history",
                "crop_stage",
                "cultivation_area",
            },
            ToolName.ENERGY: {
                "pump",
                "energy_usage",
                "irrigation_schedule",
            },
            ToolName.SUSTAINABILITY: {
                "water_usage",
                "energy_usage",
                "fertilizer_usage",
                "chemical_usage",
                "yield",
            },
            ToolName.DOCUMENT: {
                "document_id",
                "document_type",
                "document_text",
            },
            ToolName.RAG: {
                "query",
                "retrieved_documents",
                "knowledge_context",
            },
            ToolName.MARKET: {
                "market",
                "commodity",
                "market_location",
            },
            ToolName.SIMULATION: {
                "scenario",
                "simulation_parameters",
            },
        }

        allowed = common_keys | tool_specific_keys.get(
            tool_name,
            set(),
        )

        return {
            key: value
            for key, value in context.items()
            if key in allowed
        }