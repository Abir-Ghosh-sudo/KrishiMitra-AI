from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ContextSection:
    """A named section of context supplied to the AI orchestrator."""

    name: str
    data: Mapping[str, Any]

    def __post_init__(self) -> None:
        name = self.name.strip()

        if not name:
            raise ValueError("Context section name cannot be empty.")

        object.__setattr__(self, "name", name)

        if not isinstance(self.data, Mapping):
            raise TypeError("Context section data must be a mapping.")


@dataclass(frozen=True, slots=True)
class AIContext:
    """
    Structured context used during AI reasoning.

    The context is intentionally provider-independent. Database queries,
    weather calls, RAG retrieval, ML inference, and farm services should
    populate these sections before the orchestrator invokes the LLM.
    """

    farmer: Mapping[str, Any] = field(default_factory=dict)
    farm: Mapping[str, Any] = field(default_factory=dict)
    crop: Mapping[str, Any] = field(default_factory=dict)
    soil: Mapping[str, Any] = field(default_factory=dict)
    weather: Mapping[str, Any] = field(default_factory=dict)
    history: Mapping[str, Any] = field(default_factory=dict)
    diagnosis: Mapping[str, Any] = field(default_factory=dict)
    predictions: Mapping[str, Any] = field(default_factory=dict)
    rag: Mapping[str, Any] = field(default_factory=dict)
    additional: Mapping[str, Any] = field(default_factory=dict)

    def sections(self) -> tuple[ContextSection, ...]:
        """Return non-empty context sections in a stable order."""

        values = (
            ("farmer", self.farmer),
            ("farm", self.farm),
            ("crop", self.crop),
            ("soil", self.soil),
            ("weather", self.weather),
            ("history", self.history),
            ("diagnosis", self.diagnosis),
            ("predictions", self.predictions),
            ("rag", self.rag),
            ("additional", self.additional),
        )

        return tuple(
            ContextSection(name=name, data=data)
            for name, data in values
            if data
        )

    def as_mapping(self) -> dict[str, dict[str, Any]]:
        """Convert context into a serializable dictionary."""

        return {
            section.name: dict(section.data)
            for section in self.sections()
        }


class ContextBuilder:
    """
    Build immutable AI context from independently supplied sources.

    This class does not fetch data itself. That responsibility belongs to
    the relevant domain services and tool adapters.
    """

    def __init__(self) -> None:
        self._sections: dict[str, dict[str, Any]] = {}

    def add_section(
        self,
        name: str,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add or replace a named context section."""

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise ValueError(
                "Context section name cannot be empty."
            )

        if not isinstance(data, Mapping):
            raise TypeError(
                "Context section data must be a mapping."
            )

        cleaned = self._clean_mapping(data)

        if cleaned:
            self._sections[normalized_name] = cleaned

        return self

    def add_farmer(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add farmer profile/context."""

        return self.add_section("farmer", data)

    def add_farm(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add farm context."""

        return self.add_section("farm", data)

    def add_crop(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add crop and crop-stage context."""

        return self.add_section("crop", data)

    def add_soil(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add soil context."""

        return self.add_section("soil", data)

    def add_weather(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add current/forecast weather context."""

        return self.add_section("weather", data)

    def add_history(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add relevant historical farm context."""

        return self.add_section("history", data)

    def add_diagnosis(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add vision/disease/pest diagnosis context."""

        return self.add_section("diagnosis", data)

    def add_predictions(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add ML prediction results."""

        return self.add_section("predictions", data)

    def add_rag(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add retrieved agricultural knowledge."""

        return self.add_section("rag", data)

    def add_additional(
        self,
        data: Mapping[str, Any],
    ) -> "ContextBuilder":
        """Add domain-specific supplementary context."""

        return self.add_section("additional", data)

    def build(self) -> AIContext:
        """Build an immutable AI context object."""

        return AIContext(
            farmer=self._sections.get("farmer", {}),
            farm=self._sections.get("farm", {}),
            crop=self._sections.get("crop", {}),
            soil=self._sections.get("soil", {}),
            weather=self._sections.get("weather", {}),
            history=self._sections.get("history", {}),
            diagnosis=self._sections.get("diagnosis", {}),
            predictions=self._sections.get("predictions", {}),
            rag=self._sections.get("rag", {}),
            additional=self._sections.get("additional", {}),
        )

    @staticmethod
    def _clean_mapping(
        data: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Remove empty values while preserving meaningful zero/False values.

        Nested mappings are cleaned recursively. Lists and tuples are
        retained because they can represent retrieved documents, forecasts,
        diagnosis candidates, or historical observations.
        """

        cleaned: dict[str, Any] = {}

        for key, value in data.items():
            normalized_key = str(key).strip()

            if not normalized_key:
                continue

            normalized_value = ContextBuilder._clean_value(value)

            if normalized_value is not None:
                cleaned[normalized_key] = normalized_value

        return cleaned

    @staticmethod
    def _clean_value(value: Any) -> Any:
        """Normalize a single context value."""

        if value is None:
            return None

        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None

        if isinstance(value, Mapping):
            nested = ContextBuilder._clean_mapping(value)
            return nested or None

        if isinstance(value, (list, tuple)):
            normalized_items = [
                ContextBuilder._clean_value(item)
                for item in value
            ]

            normalized_items = [
                item
                for item in normalized_items
                if item is not None
            ]

            return normalized_items or None

        # Preserve valid values such as 0, 0.0, False, and UUIDs.
        return value


def merge_context(
    *contexts: AIContext,
) -> AIContext:
    """
    Merge multiple AI contexts.

    Later contexts override earlier values at the section/key level.
    """

    builder = ContextBuilder()

    for context in contexts:
        if not isinstance(context, AIContext):
            raise TypeError(
                "merge_context accepts only AIContext instances."
            )

        for section in context.sections():
            existing = builder._sections.get(
                section.name,
                {},
            )

            merged = {
                **existing,
                **dict(section.data),
            }

            builder.add_section(
                section.name,
                merged,
            )

    return builder.build()