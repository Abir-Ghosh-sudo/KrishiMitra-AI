from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Mapping


class IntentType(StrEnum):
    """High-level agricultural intents handled by KrishiMitra."""

    GENERAL_ADVISORY = "general_advisory"
    DISEASE_DIAGNOSIS = "disease_diagnosis"
    PEST_IDENTIFICATION = "pest_identification"
    WEATHER = "weather"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    SOIL_ANALYSIS = "soil_analysis"
    CROP_RECOMMENDATION = "crop_recommendation"
    CROP_STAGE = "crop_stage"
    YIELD_PREDICTION = "yield_prediction"
    SUSTAINABILITY = "sustainability"
    ENERGY_OPTIMIZATION = "energy_optimization"
    MARKET = "market"
    DOCUMENT_ANALYSIS = "document_analysis"
    FARM_STATUS = "farm_status"
    SIMULATION = "simulation"
    ALERTS = "alerts"
    EXPERT_ESCALATION = "expert_escalation"


@dataclass(frozen=True, slots=True)
class IntentCandidate:
    """One possible intent with a deterministic matching score."""

    intent: IntentType
    score: float
    matched_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "Intent score must be between 0.0 and 1.0."
            )


@dataclass(frozen=True, slots=True)
class IntentResult:
    """Final intent-routing result."""

    intent: IntentType
    confidence: float
    candidates: tuple[IntentCandidate, ...] = ()
    requires_clarification: bool = False
    clarification_reason: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Intent confidence must be between 0.0 and 1.0."
            )

        if (
            self.requires_clarification
            and not self.clarification_reason
        ):
            raise ValueError(
                "Clarification reason is required when clarification is needed."
            )


@dataclass(frozen=True, slots=True)
class IntentRule:
    """Keyword-based fallback routing rule."""

    intent: IntentType
    terms: tuple[str, ...]
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not self.terms:
            raise ValueError(
                "Intent rule must contain at least one term."
            )

        if self.weight <= 0:
            raise ValueError(
                "Intent rule weight must be greater than zero."
            )


class IntentRouter:
    """
    Deterministic first-stage intent router.

    This router is deliberately conservative. It does not claim that a
    disease, pest, or agricultural condition is actually present. It only
    identifies the likely task requested by the farmer.

    A future ML/LLM classifier can be placed before or after this component
    without changing the public result model.
    """

    DEFAULT_RULES: tuple[IntentRule, ...] = (
        IntentRule(
            IntentType.DISEASE_DIAGNOSIS,
            (
                "disease",
                "diseased",
                "infection",
                "infected",
                "leaf disease",
                "plant disease",
                "রোগ",
                "রোগ হয়েছে",
                "পাতার রোগ",
                "बीमारी",
                "रोग",
            ),
            weight=1.2,
        ),
        IntentRule(
            IntentType.PEST_IDENTIFICATION,
            (
                "pest",
                "insect",
                "bug",
                "worm",
                "caterpillar",
                "aphid",
                "borer",
                "পোকা",
                "কীট",
                "পোকামাকড়",
                "कीड़ा",
                "कीट",
            ),
            weight=1.2,
        ),
        IntentRule(
            IntentType.WEATHER,
            (
                "weather",
                "rain",
                "rainfall",
                "temperature",
                "humidity",
                "forecast",
                "বৃষ্টি",
                "আবহাওয়া",
                "তাপমাত্রা",
                "আর্দ্রতা",
                "मौसम",
                "बारिश",
            ),
            weight=1.0,
        ),
        IntentRule(
            IntentType.IRRIGATION,
            (
                "irrigation",
                "irrigate",
                "watering",
                "water the crop",
                "water requirement",
                "পানি",
                "সেচ",
                "জল",
                "সেচের",
                "सिंचाई",
                "पानी देना",
            ),
            weight=1.1,
        ),
        IntentRule(
            IntentType.FERTILIZER,
            (
                "fertilizer",
                "fertiliser",
                "urea",
                "npk",
                "nutrient",
                "manure",
                "সার",
                "ইউরিয়া",
                "পুষ্টি",
                "खाद",
                "उर्वरक",
                "यूरिया",
            ),
            weight=1.0,
        ),
        IntentRule(
            IntentType.SOIL_ANALYSIS,
            (
                "soil",
                "soil test",
                "soil report",
                "ph",
                "soil health",
                "মাটি",
                "মাটির রিপোর্ট",
                "মাটি পরীক্ষা",
                "मिट्टी",
                "मिट्टी जांच",
            ),
            weight=1.1,
        ),
        IntentRule(
            IntentType.CROP_RECOMMENDATION,
            (
                "which crop",
                "crop recommendation",
                "what should i grow",
                "best crop",
                "কোন ফসল",
                "কি চাষ",
                "কী চাষ",
                "फसल कौन",
                "कौन सी फसल",
            ),
            weight=1.2,
        ),
        IntentRule(
            IntentType.CROP_STAGE,
            (
                "crop stage",
                "growth stage",
                "flowering",
                "fruiting",
                "germination",
                "ফসলের পর্যায়",
                "বৃদ্ধির পর্যায়",
                "ফুল এসেছে",
                "ফল ধরেছে",
                "फसल अवस्था",
            ),
            weight=1.0,
        ),
        IntentRule(
            IntentType.YIELD_PREDICTION,
            (
                "yield",
                "production estimate",
                "harvest estimate",
                "yield prediction",
                "ফলন",
                "উৎপাদন",
                "কত ফলন",
                "उपज",
                "उत्पादन",
            ),
            weight=1.1,
        ),
        IntentRule(
            IntentType.SUSTAINABILITY,
            (
                "sustainability",
                "sustainable",
                "carbon",
                "carbon footprint",
                "water footprint",
                "eco friendly",
                "টেকসই",
                "কার্বন",
                "জল footprint",
                "सतत",
                "कार्बन",
            ),
            weight=1.0,
        ),
        IntentRule(
            IntentType.ENERGY_OPTIMIZATION,
            (
                "energy",
                "electricity",
                "pump energy",
                "power consumption",
                "বিদ্যুৎ",
                "এনার্জি",
                "পাম্পের বিদ্যুৎ",
                "ऊर्जा",
                "बिजली",
            ),
            weight=1.1,
        ),
        IntentRule(
            IntentType.MARKET,
            (
                "market price",
                "mandi",
                "sell crop",
                "selling price",
                "দাম",
                "বাজার",
                "ফসলের দাম",
                "मंडी",
                "बाजार भाव",
                "कीमत",
            ),
            weight=0.9,
        ),
        IntentRule(
            IntentType.DOCUMENT_ANALYSIS,
            (
                "document",
                "pdf",
                "report",
                "soil report",
                "test report",
                "রিপোর্ট",
                "ডকুমেন্ট",
                "নথি",
                "रिपोर्ट",
                "दस्तावेज",
            ),
            weight=0.9,
        ),
        IntentRule(
            IntentType.SIMULATION,
            (
                "what if",
                "what-if",
                "simulate",
                "simulation",
                "scenario",
                "যদি",
                "ধরে নিলে",
                "সিমুলেশন",
                "क्या होगा अगर",
                "सिमुलेशन",
            ),
            weight=1.1,
        ),
        IntentRule(
            IntentType.EXPERT_ESCALATION,
            (
                "expert",
                "agronomist",
                "agricultural officer",
                "human expert",
                "বিশেষজ্ঞ",
                "কৃষি অফিসার",
                "কৃষি বিশেষজ্ঞ",
                "विशेषज्ञ",
                "कृषि अधिकारी",
            ),
            weight=1.2,
        ),
        IntentRule(
            IntentType.ALERTS,
            (
                "alert",
                "alerts",
                "notification",
                "notify me",
                "reminder",
                "সতর্কতা",
                "নোটিফিকেশন",
                "মনে করিয়ে",
                "अलर्ट",
                "सूचना",
                "रिमाइंडर",
            ),
            weight=1.0,
        ),
    )

    IMAGE_HINTS = (
        "photo",
        "image",
        "picture",
        "ছবি",
        "ফটো",
        "तस्वीर",
        "फोटो",
    )

    def __init__(
        self,
        rules: Iterable[IntentRule] | None = None,
        *,
        minimum_confidence: float = 0.35,
        ambiguity_margin: float = 0.10,
    ) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError(
                "minimum_confidence must be between 0.0 and 1.0."
            )

        if ambiguity_margin < 0.0:
            raise ValueError(
                "ambiguity_margin cannot be negative."
            )

        self._rules = tuple(
            rules if rules is not None else self.DEFAULT_RULES
        )
        self.minimum_confidence = minimum_confidence
        self.ambiguity_margin = ambiguity_margin

    def route(
        self,
        text: str,
        *,
        available_modalities: Iterable[str] = (),
    ) -> IntentResult:
        """Route a farmer message to its most likely high-level intent."""

        normalized = self._normalize(text)

        if not normalized:
            raise ValueError("Intent input cannot be empty.")

        modalities = {
            str(item).strip().lower()
            for item in available_modalities
            if str(item).strip()
        }

        candidates = self._score_candidates(normalized)

        if not candidates:
            return IntentResult(
                intent=IntentType.GENERAL_ADVISORY,
                confidence=0.20,
                candidates=(),
                requires_clarification=False,
            )

        candidates = tuple(
            sorted(
                candidates,
                key=lambda candidate: candidate.score,
                reverse=True,
            )
        )

        best = candidates[0]

        if (
            "image" in modalities
            and self._contains_any(normalized, self.IMAGE_HINTS)
            and best.intent == IntentType.GENERAL_ADVISORY
        ):
            best = IntentCandidate(
                intent=IntentType.DISEASE_DIAGNOSIS,
                score=0.55,
                matched_terms=("image",),
            )

        if best.score < self.minimum_confidence:
            return IntentResult(
                intent=IntentType.GENERAL_ADVISORY,
                confidence=best.score,
                candidates=candidates,
                requires_clarification=True,
                clarification_reason=(
                    "The request does not contain enough information "
                    "to determine the intended agricultural task."
                ),
            )

        if len(candidates) > 1:
            second = candidates[1]

            if (
                best.score - second.score
                <= self.ambiguity_margin
            ):
                return IntentResult(
                    intent=best.intent,
                    confidence=best.score,
                    candidates=candidates,
                    requires_clarification=True,
                    clarification_reason=(
                        "More than one agricultural intent appears "
                        "possible."
                    ),
                )

        return IntentResult(
            intent=best.intent,
            confidence=best.score,
            candidates=candidates,
            requires_clarification=False,
        )

    def _score_candidates(
        self,
        text: str,
    ) -> tuple[IntentCandidate, ...]:
        """Score all matching intent rules."""

        scores: dict[IntentType, float] = {}
        matched: dict[IntentType, set[str]] = {}

        for rule in self._rules:
            matches = {
                term
                for term in rule.terms
                if self._term_matches(text, term)
            }

            if not matches:
                continue

            score = scores.get(rule.intent, 0.0)

            # Multiple matching terms increase confidence, but the score
            # is capped so keyword quantity cannot create artificial certainty.
            score += min(
                0.85,
                0.30 * len(matches) * rule.weight,
            )

            scores[rule.intent] = min(score, 1.0)

            matched.setdefault(
                rule.intent,
                set(),
            ).update(matches)

        return tuple(
            IntentCandidate(
                intent=intent,
                score=min(score, 1.0),
                matched_terms=tuple(
                    sorted(matched.get(intent, set()))
                ),
            )
            for intent, score in scores.items()
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize whitespace and case without changing script."""

        normalized = " ".join(text.strip().split())

        if not normalized:
            return ""

        return normalized.casefold()

    @staticmethod
    def _term_matches(
        text: str,
        term: str,
    ) -> bool:
        """Match a phrase safely without substring false positives."""

        normalized_term = " ".join(
            term.strip().split()
        ).casefold()

        if not normalized_term:
            return False

        # For Latin-script terms use word boundaries where possible.
        if re.fullmatch(
            r"[a-z0-9][a-z0-9\s\-_]*",
            normalized_term,
        ):
            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(normalized_term)
                + r"(?![a-z0-9])"
            )
            return re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            ) is not None

        return normalized_term in text

    @staticmethod
    def _contains_any(
        text: str,
        terms: Iterable[str],
    ) -> bool:
        return any(
            IntentRouter._term_matches(text, term)
            for term in terms
        )