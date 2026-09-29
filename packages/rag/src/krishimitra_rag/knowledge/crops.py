from __future__ import annotations

from dataclasses import dataclass


class CropKnowledgeError(ValueError):
    """Raised when crop knowledge operations fail."""


@dataclass(frozen=True, slots=True)
class CropKnowledge:
    """Structured agricultural knowledge about a crop."""

    crop_name: str
    scientific_name: str | None = None
    crop_family: str | None = None
    suitable_seasons: tuple[str, ...] = ()
    suitable_soil_types: tuple[str, ...] = ()
    common_growth_stages: tuple[str, ...] = ()
    water_needs: str | None = None
    temperature_range_celsius: tuple[float, float] | None = None
    common_diseases: tuple[str, ...] = ()
    common_pests: tuple[str, ...] = ()
    sustainability_notes: tuple[str, ...] = ()


class CropKnowledgeBase:
    """In-process crop knowledge registry.

    This provides a deterministic domain interface. Production knowledge
    can later be loaded from a versioned database or curated knowledge
    source without changing the consumer-facing API.
    """

    def __init__(
        self,
        crops: tuple[CropKnowledge, ...] = (),
    ) -> None:
        self._crops: dict[str, CropKnowledge] = {}

        for crop in crops:
            self.register(crop)

    def register(self, crop: CropKnowledge) -> None:
        """Register or replace crop knowledge."""
        if not isinstance(crop, CropKnowledge):
            raise CropKnowledgeError(
                "Only CropKnowledge instances can be registered"
            )

        name = self._normalize_name(crop.crop_name)

        if not name:
            raise CropKnowledgeError(
                "Crop name cannot be empty"
            )

        self._crops[name] = crop

    def get(self, crop_name: str) -> CropKnowledge:
        """Return knowledge for a crop."""
        normalized = self._normalize_name(crop_name)

        if not normalized:
            raise CropKnowledgeError(
                "Crop name cannot be empty"
            )

        try:
            return self._crops[normalized]
        except KeyError as exc:
            raise CropKnowledgeError(
                f"Crop knowledge not found: {crop_name}"
            ) from exc

    def find(self, crop_name: str) -> CropKnowledge | None:
        """Return crop knowledge when available."""
        normalized = self._normalize_name(crop_name)

        if not normalized:
            return None

        return self._crops.get(normalized)

    def list_crops(self) -> tuple[CropKnowledge, ...]:
        """Return all registered crops in deterministic order."""
        return tuple(
            self._crops[name]
            for name in sorted(self._crops)
        )

    def contains(self, crop_name: str) -> bool:
        """Check whether crop knowledge is registered."""
        return self.find(crop_name) is not None

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str):
            raise CropKnowledgeError(
                "Crop name must be a string"
            )

        return " ".join(
            name.strip().lower().split()
        )


def create_default_crop_knowledge() -> CropKnowledgeBase:
    """Create a small curated baseline crop knowledge registry."""
    crops = (
        CropKnowledge(
            crop_name="rice",
            scientific_name="Oryza sativa",
            crop_family="Poaceae",
            suitable_seasons=("kharif", "rabi"),
            suitable_soil_types=(
                "clay",
                "clay loam",
                "loam",
            ),
            common_growth_stages=(
                "seedling",
                "tillering",
                "panicle initiation",
                "flowering",
                "grain filling",
                "maturity",
            ),
            water_needs="High and stage-dependent",
            temperature_range_celsius=(20.0, 35.0),
            common_diseases=(
                "rice blast",
                "bacterial leaf blight",
                "sheath blight",
            ),
            common_pests=(
                "brown planthopper",
                "stem borer",
                "leaf folder",
            ),
            sustainability_notes=(
                "Use water management appropriate to soil and growth stage.",
                "Avoid unnecessary nitrogen application.",
            ),
        ),
        CropKnowledge(
            crop_name="wheat",
            scientific_name="Triticum aestivum",
            crop_family="Poaceae",
            suitable_seasons=("rabi",),
            suitable_soil_types=(
                "loam",
                "clay loam",
                "sandy loam",
            ),
            common_growth_stages=(
                "germination",
                "tillering",
                "stem elongation",
                "heading",
                "grain filling",
                "maturity",
            ),
            water_needs="Moderate and stage-dependent",
            temperature_range_celsius=(10.0, 25.0),
            common_diseases=(
                "wheat rust",
                "powdery mildew",
            ),
            common_pests=(
                "aphids",
                "armyworm",
            ),
            sustainability_notes=(
                "Schedule irrigation according to crop stage and rainfall.",
                "Use balanced nutrient management.",
            ),
        ),
        CropKnowledge(
            crop_name="maize",
            scientific_name="Zea mays",
            crop_family="Poaceae",
            suitable_seasons=("kharif", "rabi", "zaid"),
            suitable_soil_types=(
                "loam",
                "sandy loam",
                "clay loam",
            ),
            common_growth_stages=(
                "germination",
                "vegetative",
                "tasseling",
                "silking",
                "grain filling",
                "maturity",
            ),
            water_needs="Moderate to high during critical stages",
            temperature_range_celsius=(18.0, 32.0),
            common_diseases=(
                "maize leaf blight",
                "downy mildew",
            ),
            common_pests=(
                "fall armyworm",
                "stem borer",
            ),
            sustainability_notes=(
                "Protect water availability during tasseling and silking.",
                "Use integrated pest management before chemical intervention.",
            ),
        ),
    )

    return CropKnowledgeBase(crops)


__all__ = [
    "CropKnowledge",
    "CropKnowledgeBase",
    "CropKnowledgeError",
    "create_default_crop_knowledge",
]