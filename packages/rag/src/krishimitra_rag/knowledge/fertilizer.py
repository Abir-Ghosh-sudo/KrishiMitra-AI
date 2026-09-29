from __future__ import annotations

from dataclasses import dataclass


class FertilizerKnowledgeError(ValueError):
    """Raised when fertilizer knowledge operations fail."""


@dataclass(frozen=True, slots=True)
class FertilizerKnowledge:
    """Structured knowledge about a fertilizer or nutrient source."""

    name: str
    category: str
    primary_nutrients: tuple[str, ...] = ()
    secondary_nutrients: tuple[str, ...] = ()
    nutrient_forms: tuple[str, ...] = ()
    typical_uses: tuple[str, ...] = ()
    suitable_crops: tuple[str, ...] = ()
    application_methods: tuple[str, ...] = ()
    timing_guidance: tuple[str, ...] = ()
    compatibility_notes: tuple[str, ...] = ()
    safety_notes: tuple[str, ...] = ()
    sustainability_notes: tuple[str, ...] = ()
    source_references: tuple[str, ...] = ()


class FertilizerKnowledgeBase:
    """In-process registry for curated fertilizer knowledge."""

    def __init__(
        self,
        fertilizers: tuple[FertilizerKnowledge, ...] = (),
    ) -> None:
        self._fertilizers: dict[str, FertilizerKnowledge] = {}

        for fertilizer in fertilizers:
            self.register(fertilizer)

    def register(self, fertilizer: FertilizerKnowledge) -> None:
        """Register or replace fertilizer knowledge."""
        if not isinstance(fertilizer, FertilizerKnowledge):
            raise FertilizerKnowledgeError(
                "Only FertilizerKnowledge instances can be registered"
            )

        name = self._normalize_name(fertilizer.name)

        if not name:
            raise FertilizerKnowledgeError(
                "Fertilizer name cannot be empty"
            )

        if not fertilizer.category.strip():
            raise FertilizerKnowledgeError(
                "Fertilizer category cannot be empty"
            )

        self._fertilizers[name] = fertilizer

    def get(self, name: str) -> FertilizerKnowledge:
        """Return fertilizer knowledge."""
        normalized = self._normalize_name(name)

        if not normalized:
            raise FertilizerKnowledgeError(
                "Fertilizer name cannot be empty"
            )

        try:
            return self._fertilizers[normalized]
        except KeyError as exc:
            raise FertilizerKnowledgeError(
                f"Fertilizer knowledge not found: {name}"
            ) from exc

    def find(
        self,
        name: str,
    ) -> FertilizerKnowledge | None:
        """Return fertilizer knowledge when available."""
        normalized = self._normalize_name(name)

        if not normalized:
            return None

        return self._fertilizers.get(normalized)

    def for_crop(
        self,
        crop_name: str,
    ) -> tuple[FertilizerKnowledge, ...]:
        """Return fertilizer knowledge associated with a crop."""
        normalized_crop = self._normalize_name(crop_name)

        if not normalized_crop:
            return ()

        return tuple(
            fertilizer
            for fertilizer in self._fertilizers.values()
            if normalized_crop in {
                self._normalize_name(crop)
                for crop in fertilizer.suitable_crops
            }
        )

    def contains(self, name: str) -> bool:
        """Check whether fertilizer knowledge exists."""
        return self.find(name) is not None

    def list_fertilizers(self) -> tuple[FertilizerKnowledge, ...]:
        """Return all fertilizer entries in deterministic order."""
        return tuple(
            self._fertilizers[name]
            for name in sorted(self._fertilizers)
        )

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str):
            raise FertilizerKnowledgeError(
                "Name must be a string"
            )

        return " ".join(
            name.strip().lower().split()
        )


def create_default_fertilizer_knowledge() -> FertilizerKnowledgeBase:
    """Create a small curated baseline fertilizer knowledge registry."""
    fertilizers = (
        FertilizerKnowledge(
            name="urea",
            category="nitrogen fertilizer",
            primary_nutrients=("nitrogen",),
            nutrient_forms=("amide nitrogen",),
            typical_uses=(
                "Nitrogen supplementation where soil and crop assessment indicates a need",
            ),
            suitable_crops=(
                "rice",
                "wheat",
                "maize",
            ),
            application_methods=(
                "Soil application according to an agronomic recommendation",
            ),
            timing_guidance=(
                "Nitrogen should be split and timed according to crop stage and local recommendations.",
            ),
            compatibility_notes=(
                "Avoid indiscriminate mixing with incompatible products.",
            ),
            safety_notes=(
                "Application quantity must be based on soil test, crop requirement, and local recommendation.",
                "Avoid unnecessary application before heavy rainfall.",
            ),
            sustainability_notes=(
                "Avoid excess nitrogen to reduce nutrient losses and emissions.",
                "Use split application where agronomically appropriate.",
            ),
        ),
        FertilizerKnowledge(
            name="diammonium phosphate",
            category="compound fertilizer",
            primary_nutrients=(
                "nitrogen",
                "phosphorus",
            ),
            nutrient_forms=(
                "ammoniacal nitrogen",
                "phosphate",
            ),
            typical_uses=(
                "Basal phosphorus and nitrogen supply where soil testing supports the need",
            ),
            suitable_crops=(
                "rice",
                "wheat",
                "maize",
            ),
            application_methods=(
                "Soil application according to crop-specific nutrient recommendations",
            ),
            timing_guidance=(
                "Phosphorus is generally planned around establishment and root development.",
            ),
            compatibility_notes=(
                "Compatibility depends on the other fertilizer or amendment.",
            ),
            safety_notes=(
                "Do not infer application rates without soil and crop context.",
            ),
            sustainability_notes=(
                "Use soil-test-based phosphorus management to reduce nutrient losses.",
            ),
        ),
        FertilizerKnowledge(
            name="muriate of potash",
            category="potassium fertilizer",
            primary_nutrients=("potassium",),
            nutrient_forms=("potassium chloride",),
            typical_uses=(
                "Potassium supplementation where soil and crop requirements indicate a deficiency or need",
            ),
            suitable_crops=(
                "rice",
                "wheat",
                "maize",
            ),
            application_methods=(
                "Soil application according to agronomic recommendation",
            ),
            timing_guidance=(
                "Application timing should follow crop-specific potassium requirements.",
            ),
            compatibility_notes=(
                "Consider crop sensitivity to chloride when selecting potassium sources.",
            ),
            safety_notes=(
                "Rate should be determined from soil testing and crop nutrient requirements.",
            ),
            sustainability_notes=(
                "Avoid excessive potassium application when soil reserves are already adequate.",
            ),
        ),
        FertilizerKnowledge(
            name="farmyard manure",
            category="organic amendment",
            primary_nutrients=(
                "nitrogen",
                "phosphorus",
                "potassium",
            ),
            typical_uses=(
                "Improving soil organic matter",
                "Supporting nutrient supply",
                "Improving soil structure",
            ),
            suitable_crops=(
                "rice",
                "wheat",
                "maize",
            ),
            application_methods=(
                "Incorporation into soil before or around crop establishment",
            ),
            timing_guidance=(
                "Use well-decomposed material and apply according to local agronomic practice.",
            ),
            compatibility_notes=(
                "Nutrient content varies substantially with source and decomposition.",
            ),
            safety_notes=(
                "Use properly decomposed organic material to reduce contamination risks.",
            ),
            sustainability_notes=(
                "Can improve soil organic matter and nutrient cycling when appropriately managed.",
            ),
        ),
    )

    return FertilizerKnowledgeBase(fertilizers)


__all__ = [
    "FertilizerKnowledge",
    "FertilizerKnowledgeBase",
    "FertilizerKnowledgeError",
    "create_default_fertilizer_knowledge",
]