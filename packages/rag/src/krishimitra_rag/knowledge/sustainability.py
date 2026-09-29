from __future__ import annotations

from dataclasses import dataclass


class SustainabilityKnowledgeError(ValueError):
    """Raised when sustainability knowledge operations fail."""


@dataclass(frozen=True, slots=True)
class SustainabilityKnowledge:
    """Structured sustainability guidance for agricultural practices."""

    topic: str
    description: str
    practices: tuple[str, ...] = ()
    benefits: tuple[str, ...] = ()
    risks_or_tradeoffs: tuple[str, ...] = ()
    indicators: tuple[str, ...] = ()
    applicable_crops: tuple[str, ...] = ()
    source_references: tuple[str, ...] = ()


class SustainabilityKnowledgeBase:
    """In-process registry for curated sustainability knowledge."""

    def __init__(
        self,
        entries: tuple[SustainabilityKnowledge, ...] = (),
    ) -> None:
        self._entries: dict[str, SustainabilityKnowledge] = {}

        for entry in entries:
            self.register(entry)

    def register(self, entry: SustainabilityKnowledge) -> None:
        """Register or replace sustainability knowledge."""
        if not isinstance(entry, SustainabilityKnowledge):
            raise SustainabilityKnowledgeError(
                "Only SustainabilityKnowledge instances can be registered"
            )

        topic = self._normalize_name(entry.topic)

        if not topic:
            raise SustainabilityKnowledgeError(
                "Sustainability topic cannot be empty"
            )

        if not entry.description.strip():
            raise SustainabilityKnowledgeError(
                "Sustainability description cannot be empty"
            )

        self._entries[topic] = entry

    def get(self, topic: str) -> SustainabilityKnowledge:
        """Return knowledge for a sustainability topic."""
        normalized = self._normalize_name(topic)

        if not normalized:
            raise SustainabilityKnowledgeError(
                "Sustainability topic cannot be empty"
            )

        try:
            return self._entries[normalized]
        except KeyError as exc:
            raise SustainabilityKnowledgeError(
                f"Sustainability knowledge not found: {topic}"
            ) from exc

    def find(
        self,
        topic: str,
    ) -> SustainabilityKnowledge | None:
        """Return topic knowledge when available."""
        normalized = self._normalize_name(topic)

        if not normalized:
            return None

        return self._entries.get(normalized)

    def for_crop(
        self,
        crop_name: str,
    ) -> tuple[SustainabilityKnowledge, ...]:
        """Return sustainability topics applicable to a crop."""
        normalized_crop = self._normalize_name(crop_name)

        if not normalized_crop:
            return ()

        return tuple(
            entry
            for entry in self._entries.values()
            if not entry.applicable_crops
            or normalized_crop in {
                self._normalize_name(crop)
                for crop in entry.applicable_crops
            }
        )

    def contains(self, topic: str) -> bool:
        """Check whether a sustainability topic exists."""
        return self.find(topic) is not None

    def list_topics(self) -> tuple[SustainabilityKnowledge, ...]:
        """Return all topics in deterministic order."""
        return tuple(
            self._entries[topic]
            for topic in sorted(self._entries)
        )

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str):
            raise SustainabilityKnowledgeError(
                "Name must be a string"
            )

        return " ".join(
            name.strip().lower().split()
        )


def create_default_sustainability_knowledge() -> (
    SustainabilityKnowledgeBase
):
    """Create a curated baseline sustainability knowledge registry."""
    entries = (
        SustainabilityKnowledge(
            topic="water efficiency",
            description=(
                "Improving crop water productivity while maintaining "
                "appropriate crop health and yield."
            ),
            practices=(
                "Use weather-aware irrigation scheduling.",
                "Account for rainfall before irrigation.",
                "Use crop-stage-specific water requirements.",
                "Avoid unnecessary irrigation.",
                "Monitor soil moisture where reliable measurements are available.",
            ),
            benefits=(
                "Reduced water consumption",
                "Lower irrigation energy demand",
                "Improved water productivity",
            ),
            risks_or_tradeoffs=(
                "Under-irrigation can reduce crop growth and yield.",
                "Water requirements vary with crop, soil, weather, and growth stage.",
            ),
            indicators=(
                "Water used per unit of production",
                "Irrigation frequency",
                "Estimated crop water requirement",
                "Rainfall contribution",
            ),
            applicable_crops=(
                "rice",
                "wheat",
                "maize",
            ),
        ),
        SustainabilityKnowledge(
            topic="nitrogen efficiency",
            description=(
                "Managing nitrogen inputs according to crop demand "
                "to reduce nutrient losses and unnecessary emissions."
            ),
            practices=(
                "Use soil-test-informed nutrient planning.",
                "Match nitrogen application with crop stage.",
                "Prefer split application where agronomically appropriate.",
                "Account for weather and rainfall risk.",
            ),
            benefits=(
                "Reduced nitrogen losses",
                "Improved nutrient-use efficiency",
                "Potential reduction in nitrogen-related emissions",
            ),
            risks_or_tradeoffs=(
                "Insufficient nitrogen can reduce crop productivity.",
                "Nitrogen requirements vary with soil fertility and yield target.",
            ),
            indicators=(
                "Nitrogen applied per hectare",
                "Estimated crop nitrogen requirement",
                "Nitrogen-use efficiency",
            ),
            applicable_crops=(
                "rice",
                "wheat",
                "maize",
            ),
        ),
        SustainabilityKnowledge(
            topic="integrated pest management",
            description=(
                "Combining monitoring, cultural, mechanical, biological, "
                "and justified chemical controls to manage agricultural pests."
            ),
            practices=(
                "Scout fields regularly.",
                "Use pest identification and threshold-based decisions.",
                "Conserve beneficial organisms.",
                "Prefer non-chemical controls where effective.",
                "Use approved chemical products only when justified.",
            ),
            benefits=(
                "Reduced unnecessary pesticide use",
                "Lower resistance pressure",
                "Protection of beneficial organisms",
            ),
            risks_or_tradeoffs=(
                "Monitoring requires regular field observation.",
                "Control effectiveness varies by pest and local conditions.",
            ),
            indicators=(
                "Pest incidence",
                "Intervention frequency",
                "Chemical application frequency",
                "Natural-enemy observations",
            ),
        ),
        SustainabilityKnowledge(
            topic="soil health",
            description=(
                "Maintaining soil structure, organic matter, nutrient balance, "
                "and biological activity for long-term agricultural productivity."
            ),
            practices=(
                "Use soil-test-based nutrient management.",
                "Return suitable organic matter to the soil.",
                "Avoid unnecessary nutrient application.",
                "Maintain suitable crop rotation where practical.",
                "Reduce avoidable soil disturbance.",
            ),
            benefits=(
                "Improved soil structure",
                "Better nutrient cycling",
                "Improved long-term productivity",
            ),
            risks_or_tradeoffs=(
                "Soil-health practices may require changes in farm operations.",
                "Benefits can take multiple seasons to become measurable.",
            ),
            indicators=(
                "Soil organic matter",
                "Soil nutrient status",
                "pH",
                "Bulk density",
                "Water-holding characteristics",
            ),
        ),
        SustainabilityKnowledge(
            topic="energy efficiency",
            description=(
                "Reducing unnecessary energy use associated with irrigation "
                "and other farm operations while maintaining required output."
            ),
            practices=(
                "Schedule irrigation according to actual crop water demand.",
                "Avoid unnecessary pumping.",
                "Consider rainfall before irrigation.",
                "Track pump runtime and energy consumption where available.",
            ),
            benefits=(
                "Reduced electricity or fuel consumption",
                "Lower operating cost",
                "Lower associated emissions",
            ),
            risks_or_tradeoffs=(
                "Energy savings must not compromise crop water requirements.",
                "Energy estimates depend on pump and irrigation-system characteristics.",
            ),
            indicators=(
                "Pump runtime",
                "Energy consumed per irrigation event",
                "Energy per unit of production",
                "Water delivered per unit of energy",
            ),
        ),
        SustainabilityKnowledge(
            topic="crop rotation",
            description=(
                "Planned sequencing of different crops across seasons "
                "to support soil health and reduce recurring biological risks."
            ),
            practices=(
                "Rotate crops with different nutrient requirements.",
                "Include suitable crops that interrupt pest and disease cycles.",
                "Consider local climate, soil, market, and water constraints.",
            ),
            benefits=(
                "Improved soil-health management",
                "Potential reduction in recurring pest and disease pressure",
                "More balanced nutrient use",
            ),
            risks_or_tradeoffs=(
                "Rotation choices depend on local agronomic and economic conditions.",
                "Market demand may limit practical rotation options.",
            ),
            indicators=(
                "Crop diversity across seasons",
                "Disease recurrence",
                "Pest recurrence",
                "Soil nutrient trends",
            ),
        ),
        SustainabilityKnowledge(
            topic="carbon efficiency",
            description=(
                "Reducing avoidable greenhouse-gas emissions associated with "
                "farm inputs, energy, water, and management decisions."
            ),
            practices=(
                "Reduce unnecessary nitrogen inputs.",
                "Improve irrigation efficiency.",
                "Reduce unnecessary pumping.",
                "Maintain soil organic matter where appropriate.",
                "Use farm-specific activity data for carbon estimation.",
            ),
            benefits=(
                "Potential reduction in farm-associated emissions",
                "Improved resource efficiency",
                "Better climate-impact visibility",
            ),
            risks_or_tradeoffs=(
                "Carbon estimates are sensitive to emission-factor assumptions.",
                "Carbon metrics should report uncertainty rather than false precision.",
            ),
            indicators=(
                "Estimated emissions per hectare",
                "Estimated emissions per unit of production",
                "Energy consumption",
                "Nitrogen input",
                "Water and irrigation energy use",
            ),
        ),
    )

    return SustainabilityKnowledgeBase(entries)


__all__ = [
    "SustainabilityKnowledge",
    "SustainabilityKnowledgeBase",
    "SustainabilityKnowledgeError",
    "create_default_sustainability_knowledge",
]