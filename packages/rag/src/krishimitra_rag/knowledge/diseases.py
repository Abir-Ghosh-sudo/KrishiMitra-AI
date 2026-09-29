from __future__ import annotations

from dataclasses import dataclass


class DiseaseKnowledgeError(ValueError):
    """Raised when disease knowledge operations fail."""


@dataclass(frozen=True, slots=True)
class DiseaseKnowledge:
    """Structured knowledge about an agricultural plant disease."""

    disease_name: str
    scientific_name: str | None = None
    affected_crops: tuple[str, ...] = ()
    symptoms: tuple[str, ...] = ()
    contributing_factors: tuple[str, ...] = ()
    favorable_conditions: tuple[str, ...] = ()
    severity_indicators: tuple[str, ...] = ()
    prevention_measures: tuple[str, ...] = ()
    cultural_controls: tuple[str, ...] = ()
    biological_controls: tuple[str, ...] = ()
    chemical_control_notes: tuple[str, ...] = ()
    source_references: tuple[str, ...] = ()


class DiseaseKnowledgeBase:
    """In-process registry for curated agricultural disease knowledge."""

    def __init__(
        self,
        diseases: tuple[DiseaseKnowledge, ...] = (),
    ) -> None:
        self._diseases: dict[str, DiseaseKnowledge] = {}

        for disease in diseases:
            self.register(disease)

    def register(self, disease: DiseaseKnowledge) -> None:
        """Register or replace disease knowledge."""
        if not isinstance(disease, DiseaseKnowledge):
            raise DiseaseKnowledgeError(
                "Only DiseaseKnowledge instances can be registered"
            )

        name = self._normalize_name(disease.disease_name)

        if not name:
            raise DiseaseKnowledgeError(
                "Disease name cannot be empty"
            )

        self._diseases[name] = disease

    def get(self, disease_name: str) -> DiseaseKnowledge:
        """Return knowledge for a disease."""
        normalized = self._normalize_name(disease_name)

        if not normalized:
            raise DiseaseKnowledgeError(
                "Disease name cannot be empty"
            )

        try:
            return self._diseases[normalized]
        except KeyError as exc:
            raise DiseaseKnowledgeError(
                f"Disease knowledge not found: {disease_name}"
            ) from exc

    def find(
        self,
        disease_name: str,
    ) -> DiseaseKnowledge | None:
        """Return disease knowledge when available."""
        normalized = self._normalize_name(disease_name)

        if not normalized:
            return None

        return self._diseases.get(normalized)

    def for_crop(
        self,
        crop_name: str,
    ) -> tuple[DiseaseKnowledge, ...]:
        """Return diseases associated with a crop."""
        normalized_crop = self._normalize_name(crop_name)

        if not normalized_crop:
            return ()

        return tuple(
            disease
            for disease in self._diseases.values()
            if normalized_crop in {
                self._normalize_name(crop)
                for crop in disease.affected_crops
            }
        )

    def contains(self, disease_name: str) -> bool:
        """Check whether disease knowledge exists."""
        return self.find(disease_name) is not None

    def list_diseases(self) -> tuple[DiseaseKnowledge, ...]:
        """Return all diseases in deterministic order."""
        return tuple(
            self._diseases[name]
            for name in sorted(self._diseases)
        )

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str):
            raise DiseaseKnowledgeError(
                "Name must be a string"
            )

        return " ".join(
            name.strip().lower().split()
        )


def create_default_disease_knowledge() -> DiseaseKnowledgeBase:
    """Create a small curated baseline disease knowledge registry."""
    diseases = (
        DiseaseKnowledge(
            disease_name="rice blast",
            scientific_name="Magnaporthe oryzae",
            affected_crops=("rice",),
            symptoms=(
                "Spindle-shaped lesions on leaves",
                "Lesions may develop gray centers",
                "Neck or panicle infection can reduce grain formation",
            ),
            contributing_factors=(
                "High humidity",
                "Leaf wetness",
                "Dense crop canopy",
                "Excessive nitrogen",
            ),
            favorable_conditions=(
                "Warm and humid conditions",
                "Frequent leaf wetness",
            ),
            severity_indicators=(
                "Increasing number of lesions",
                "Rapid lesion expansion",
                "Panicle or neck involvement",
            ),
            prevention_measures=(
                "Use appropriate crop spacing",
                "Maintain balanced nitrogen nutrition",
                "Use disease-free seed",
            ),
            cultural_controls=(
                "Remove heavily infected plant residue where appropriate",
                "Avoid unnecessary excessive nitrogen",
            ),
            biological_controls=(
                "Consider locally validated biological disease-management options",
            ),
            chemical_control_notes=(
                "Chemical control must follow the locally approved product label and crop registration.",
                "Application timing should account for weather and disease stage.",
            ),
        ),
        DiseaseKnowledge(
            disease_name="bacterial leaf blight",
            scientific_name="Xanthomonas oryzae pv. oryzae",
            affected_crops=("rice",),
            symptoms=(
                "Water-soaked leaf lesions",
                "Yellowing and drying of leaf margins",
                "Lesions may extend along leaf veins",
            ),
            contributing_factors=(
                "High humidity",
                "Rain and wind-driven water",
                "Excess nitrogen",
                "Plant injury",
            ),
            favorable_conditions=(
                "Warm humid weather",
                "Frequent rainfall",
            ),
            severity_indicators=(
                "Rapid expansion of leaf lesions",
                "Large proportion of affected foliage",
                "Wilting of young plants in severe cases",
            ),
            prevention_measures=(
                "Use healthy seed",
                "Maintain balanced fertilizer management",
                "Avoid unnecessary plant injury",
            ),
            cultural_controls=(
                "Maintain suitable field water management",
                "Avoid excessive nitrogen application",
            ),
            biological_controls=(
                "Use only locally validated biological control products or practices.",
            ),
            chemical_control_notes=(
                "Do not provide a chemical recommendation without crop, location, diagnosis confidence, and current label information.",
            ),
        ),
        DiseaseKnowledge(
            disease_name="wheat rust",
            affected_crops=("wheat",),
            symptoms=(
                "Rust-colored pustules on leaves or stems",
                "Progressive loss of green leaf area",
            ),
            contributing_factors=(
                "Suitable temperature and humidity",
                "Susceptible crop variety",
            ),
            favorable_conditions=(
                "Moderate temperatures",
                "Leaf wetness",
            ),
            severity_indicators=(
                "Increasing pustule density",
                "Spread to upper leaves",
                "Premature leaf senescence",
            ),
            prevention_measures=(
                "Use resistant or locally recommended varieties",
                "Monitor fields regularly",
            ),
            cultural_controls=(
                "Use recommended sowing time",
                "Maintain balanced crop nutrition",
            ),
            biological_controls=(
                "Use locally validated biological options where available.",
            ),
            chemical_control_notes=(
                "Any fungicide recommendation must be based on current local registration and label directions.",
            ),
        ),
    )

    return DiseaseKnowledgeBase(diseases)


__all__ = [
    "DiseaseKnowledge",
    "DiseaseKnowledgeBase",
    "DiseaseKnowledgeError",
    "create_default_disease_knowledge",
]