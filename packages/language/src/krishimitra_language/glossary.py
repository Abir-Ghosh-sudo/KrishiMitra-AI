"""Agricultural terminology glossary for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GlossaryCategory(StrEnum):
    """Categories used to organize agricultural terminology."""

    CROP = "crop"
    SOIL = "soil"
    WATER = "water"
    WEATHER = "weather"
    DISEASE = "disease"
    PEST = "pest"
    FERTILIZER = "fertilizer"
    IRRIGATION = "irrigation"
    SUSTAINABILITY = "sustainability"
    GENERAL = "general"


@dataclass(frozen=True, slots=True)
class GlossaryEntry:
    """Canonical agricultural term and its localized equivalents."""

    key: str
    category: GlossaryCategory
    canonical: str
    translations: dict[str, str]
    aliases: tuple[str, ...] = ()

    def translation(
        self,
        language: str,
    ) -> str:
        """Return a translation or the canonical term as fallback."""

        return self.translations.get(
            language.lower(),
            self.canonical,
        )


_GLOSSARY: tuple[GlossaryEntry, ...] = (
    GlossaryEntry(
        key="crop",
        category=GlossaryCategory.CROP,
        canonical="crop",
        translations={
            "en": "crop",
            "bn": "ফসল",
            "hi": "फसल",
            "or": "ଫସଲ",
            "ta": "பயிர்",
            "te": "పంట",
            "mr": "पीक",
            "gu": "પાક",
        },
        aliases=("crops", "fasal", "foshol"),
    ),
    GlossaryEntry(
        key="soil",
        category=GlossaryCategory.SOIL,
        canonical="soil",
        translations={
            "en": "soil",
            "bn": "মাটি",
            "hi": "मिट्टी",
            "or": "ମାଟି",
            "ta": "மண்",
            "te": "నేల",
            "mr": "माती",
            "gu": "માટી",
        },
        aliases=("land", "mati", "mitti"),
    ),
    GlossaryEntry(
        key="water",
        category=GlossaryCategory.WATER,
        canonical="water",
        translations={
            "en": "water",
            "bn": "জল",
            "hi": "पानी",
            "or": "ପାଣି",
            "ta": "தண்ணீர்",
            "te": "నీరు",
            "mr": "पाणी",
            "gu": "પાણી",
        },
        aliases=("pani", "jal"),
    ),
    GlossaryEntry(
        key="irrigation",
        category=GlossaryCategory.IRRIGATION,
        canonical="irrigation",
        translations={
            "en": "irrigation",
            "bn": "সেচ",
            "hi": "सिंचाई",
            "or": "ଜଳସେଚନ",
            "ta": "நீர்ப்பாசனம்",
            "te": "నీటిపారుదల",
            "mr": "सिंचन",
            "gu": "સિંચાઈ",
        },
        aliases=("irrigate", "sinchai", "sech"),
    ),
    GlossaryEntry(
        key="fertilizer",
        category=GlossaryCategory.FERTILIZER,
        canonical="fertilizer",
        translations={
            "en": "fertilizer",
            "bn": "সার",
            "hi": "उर्वरक",
            "or": "ସାର",
            "ta": "உரம்",
            "te": "ఎరువు",
            "mr": "खत",
            "gu": "ખાતર",
        },
        aliases=("fertiliser", "sar", "khat"),
    ),
    GlossaryEntry(
        key="pest",
        category=GlossaryCategory.PEST,
        canonical="pest",
        translations={
            "en": "pest",
            "bn": "পোকা",
            "hi": "कीट",
            "or": "କୀଟ",
            "ta": "பூச்சி",
            "te": "చీడపీడ",
            "mr": "कीड",
            "gu": "જીવાત",
        },
        aliases=("insect", "poka", "keet"),
    ),
    GlossaryEntry(
        key="disease",
        category=GlossaryCategory.DISEASE,
        canonical="disease",
        translations={
            "en": "disease",
            "bn": "রোগ",
            "hi": "रोग",
            "or": "ରୋଗ",
            "ta": "நோய்",
            "te": "వ్యాధి",
            "mr": "रोग",
            "gu": "રોગ",
        },
        aliases=("plant disease", "rog"),
    ),
    GlossaryEntry(
        key="rain",
        category=GlossaryCategory.WEATHER,
        canonical="rain",
        translations={
            "en": "rain",
            "bn": "বৃষ্টি",
            "hi": "बारिश",
            "or": "ବର୍ଷା",
            "ta": "மழை",
            "te": "వర్షం",
            "mr": "पाऊस",
            "gu": "વરસાદ",
        },
        aliases=("rainfall", "bristi", "barish"),
    ),
    GlossaryEntry(
        key="yield",
        category=GlossaryCategory.CROP,
        canonical="yield",
        translations={
            "en": "yield",
            "bn": "ফলন",
            "hi": "उपज",
            "or": "ଅମଳ",
            "ta": "மகசூல்",
            "te": "దిగుబడి",
            "mr": "उत्पन्न",
            "gu": "ઉપજ",
        },
        aliases=("production", "folon", "upaj"),
    ),
    GlossaryEntry(
        key="sustainability",
        category=GlossaryCategory.SUSTAINABILITY,
        canonical="sustainability",
        translations={
            "en": "sustainability",
            "bn": "স্থায়িত্ব",
            "hi": "स्थिरता",
            "or": "ସ୍ଥାୟୀତ୍ୱ",
            "ta": "நிலைத்தன்மை",
            "te": "సుస్థిరత",
            "mr": "शाश्वतता",
            "gu": "ટકાઉપણું",
        },
        aliases=("sustainable farming", "sustainable agriculture"),
    ),
)


class AgriculturalGlossary:
    """Lookup service for canonical agricultural terminology."""

    def __init__(
        self,
        entries: tuple[GlossaryEntry, ...] = _GLOSSARY,
    ) -> None:
        self._entries = {
            entry.key: entry
            for entry in entries
        }

        self._aliases = {
            alias.casefold(): entry.key
            for entry in entries
            for alias in entry.aliases
        }

    def get(
        self,
        key: str,
    ) -> GlossaryEntry | None:
        """Return an entry by canonical key or alias."""

        normalized = key.strip().casefold()

        if normalized in self._entries:
            return self._entries[normalized]

        canonical_key = self._aliases.get(normalized)

        if canonical_key is None:
            return None

        return self._entries[canonical_key]

    def translate(
        self,
        key: str,
        language: str,
    ) -> str | None:
        """Translate a glossary term into a requested language."""

        entry = self.get(key)

        if entry is None:
            return None

        return entry.translation(language)

    def by_category(
        self,
        category: GlossaryCategory,
    ) -> tuple[GlossaryEntry, ...]:
        """Return all entries belonging to a category."""

        return tuple(
            entry
            for entry in self._entries.values()
            if entry.category is category
        )

    def keys(self) -> tuple[str, ...]:
        """Return all canonical glossary keys."""

        return tuple(self._entries.keys())

    def __len__(self) -> int:
        """Return the number of glossary entries."""

        return len(self._entries)


def get_glossary() -> AgriculturalGlossary:
    """Return the default agricultural glossary."""

    return AgriculturalGlossary()


__all__ = [
    "AgriculturalGlossary",
    "GlossaryCategory",
    "GlossaryEntry",
    "get_glossary",
]