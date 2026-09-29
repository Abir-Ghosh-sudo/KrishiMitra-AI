from __future__ import annotations

from dataclasses import dataclass


class PestKnowledgeError(ValueError):
    """Raised when pest knowledge operations fail."""


@dataclass(frozen=True, slots=True)
class PestKnowledge:
    """Structured knowledge about an agricultural pest."""

    pest_name: str
    scientific_name: str | None = None
    affected_crops: tuple[str, ...] = ()
    identification_features: tuple[str, ...] = ()
    damage_symptoms: tuple[str, ...] = ()
    favorable_conditions: tuple[str, ...] = ()
    risk_factors: tuple[str, ...] = ()
    monitoring_methods: tuple[str, ...] = ()
    cultural_controls: tuple[str, ...] = ()
    mechanical_controls: tuple[str, ...] = ()
    biological_controls: tuple[str, ...] = ()
    chemical_control_notes: tuple[str, ...] = ()
    integrated_management: tuple[str, ...] = ()
    source_references: tuple[str, ...] = ()


class PestKnowledgeBase:
    """In-process registry for curated agricultural pest knowledge."""

    def __init__(
        self,
        pests: tuple[PestKnowledge, ...] = (),
    ) -> None:
        self._pests: dict[str, PestKnowledge] = {}

        for pest in pests:
            self.register(pest)

    def register(self, pest: PestKnowledge) -> None:
        """Register or replace pest knowledge."""
        if not isinstance(pest, PestKnowledge):
            raise PestKnowledgeError(
                "Only PestKnowledge instances can be registered"
            )

        name = self._normalize_name(pest.pest_name)

        if not name:
            raise PestKnowledgeError(
                "Pest name cannot be empty"
            )

        self._pests[name] = pest

    def get(self, pest_name: str) -> PestKnowledge:
        """Return knowledge for a pest."""
        normalized = self._normalize_name(pest_name)

        if not normalized:
            raise PestKnowledgeError(
                "Pest name cannot be empty"
            )

        try:
            return self._pests[normalized]
        except KeyError as exc:
            raise PestKnowledgeError(
                f"Pest knowledge not found: {pest_name}"
            ) from exc

    def find(
        self,
        pest_name: str,
    ) -> PestKnowledge | None:
        """Return pest knowledge when available."""
        normalized = self._normalize_name(pest_name)

        if not normalized:
            return None

        return self._pests.get(normalized)

    def for_crop(
        self,
        crop_name: str,
    ) -> tuple[PestKnowledge, ...]:
        """Return pests associated with a crop."""
        normalized_crop = self._normalize_name(crop_name)

        if not normalized_crop:
            return ()

        return tuple(
            pest
            for pest in self._pests.values()
            if normalized_crop in {
                self._normalize_name(crop)
                for crop in pest.affected_crops
            }
        )

    def contains(self, pest_name: str) -> bool:
        """Check whether pest knowledge exists."""
        return self.find(pest_name) is not None

    def list_pests(self) -> tuple[PestKnowledge, ...]:
        """Return all registered pests in deterministic order."""
        return tuple(
            self._pests[name]
            for name in sorted(self._pests)
        )

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str):
            raise PestKnowledgeError(
                "Name must be a string"
            )

        return " ".join(
            name.strip().lower().split()
        )


def create_default_pest_knowledge() -> PestKnowledgeBase:
    """Create a small curated baseline pest knowledge registry."""
    pests = (
        PestKnowledge(
            pest_name="brown planthopper",
            scientific_name="Nilaparvata lugens",
            affected_crops=("rice",),
            identification_features=(
                "Small planthoppers occurring near the plant base",
                "Adults may be brownish with winged or wingless forms",
            ),
            damage_symptoms=(
                "Yellowing of rice plants",
                "Patchy drying or hopperburn under severe infestation",
            ),
            favorable_conditions=(
                "Warm humid conditions",
                "Dense crop canopy",
                "Excessive nitrogen",
            ),
            risk_factors=(
                "Repeated insecticide use that disrupts natural enemies",
                "Excessive nitrogen application",
                "Dense planting",
            ),
            monitoring_methods=(
                "Regular field scouting",
                "Check the plant base for insects",
                "Monitor population trends before intervention",
            ),
            cultural_controls=(
                "Avoid excessive nitrogen",
                "Maintain appropriate plant spacing",
            ),
            mechanical_controls=(
                "Use field scouting and removal of heavily affected areas where practical",
            ),
            biological_controls=(
                "Conserve natural enemies",
                "Use locally validated biological control approaches",
            ),
            chemical_control_notes=(
                "Use insecticides only when justified by local thresholds and current label guidance.",
                "Rotate compatible modes of action to reduce resistance risk.",
            ),
            integrated_management=(
                "Prioritize monitoring and conservation of natural enemies before chemical intervention.",
            ),
        ),
        PestKnowledge(
            pest_name="stem borer",
            affected_crops=("rice", "maize"),
            identification_features=(
                "Larval feeding occurs inside plant stems",
                "Adult moths may be observed around the crop",
            ),
            damage_symptoms=(
                "Dead hearts in vegetative stages",
                "White heads or damaged reproductive structures",
                "Stem tunneling",
            ),
            favorable_conditions=(
                "Warm conditions",
                "Continuous availability of host plants",
            ),
            risk_factors=(
                "Continuous cropping",
                "Poor field sanitation",
            ),
            monitoring_methods=(
                "Regular scouting for dead hearts",
                "Inspect stems and affected tillers",
            ),
            cultural_controls=(
                "Maintain field sanitation",
                "Use locally recommended planting practices",
            ),
            mechanical_controls=(
                "Remove severely affected plant material where practical",
            ),
            biological_controls=(
                "Conserve parasitoids and predators",
                "Use locally validated biological control methods",
            ),
            chemical_control_notes=(
                "Chemical control should be based on local pest thresholds and approved product labels.",
            ),
            integrated_management=(
                "Combine crop monitoring, cultural measures, biological control, and justified chemical intervention.",
            ),
        ),
        PestKnowledge(
            pest_name="fall armyworm",
            scientific_name="Spodoptera frugiperda",
            affected_crops=("maize",),
            identification_features=(
                "Caterpillars may show characteristic markings on the head and body",
                "Larvae often feed within the maize whorl",
            ),
            damage_symptoms=(
                "Windowing and holes in young leaves",
                "Ragged feeding damage",
                "Frass inside the whorl",
            ),
            favorable_conditions=(
                "Warm weather",
                "Suitable host availability",
            ),
            risk_factors=(
                "Continuous maize cultivation",
                "Late detection",
            ),
            monitoring_methods=(
                "Inspect maize whorls regularly",
                "Monitor young plants for feeding damage",
            ),
            cultural_controls=(
                "Maintain timely crop establishment",
                "Remove heavily infested plant material where appropriate",
            ),
            mechanical_controls=(
                "Physically remove larvae from localized infestations where practical",
            ),
            biological_controls=(
                "Conserve parasitoids and predators",
                "Use locally validated biological products when appropriate",
            ),
            chemical_control_notes=(
                "Use only currently approved products and label directions for the crop and location.",
                "Avoid repeated use of the same mode of action.",
            ),
            integrated_management=(
                "Use early scouting and integrated pest management before relying on chemical control.",
            ),
        ),
    )

    return PestKnowledgeBase(pests)


__all__ = [
    "PestKnowledge",
    "PestKnowledgeBase",
    "PestKnowledgeError",
    "create_default_pest_knowledge",
]