"""Agricultural market intelligence models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MarketPriceSource(StrEnum):
    """Sources used for agricultural market prices."""

    GOVERNMENT = "government"
    MARKET = "market"
    VERIFIED_PROVIDER = "verified_provider"
    USER_REPORTED = "user_reported"


class MarketTrend(StrEnum):
    """Observed or predicted market trend."""

    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    UNKNOWN = "unknown"


class MarketPrice(BaseModel):
    """Market price observation for an agricultural commodity."""

    model_config = ConfigDict(extra="forbid")

    price_id: UUID

    crop_name: str = Field(min_length=1, max_length=200)
    market_name: str = Field(min_length=1, max_length=200)

    observed_at: datetime

    price_per_quintal_inr: float = Field(ge=0.0)

    source: MarketPriceSource

    currency: str = Field(default="INR", min_length=3, max_length=3)

    trend: MarketTrend = MarketTrend.UNKNOWN


class MarketInsight(BaseModel):
    """Derived market intelligence for a farmer."""

    model_config = ConfigDict(extra="forbid")

    insight_id: UUID
    farm_id: UUID | None = None

    crop_name: str = Field(min_length=1, max_length=200)

    current_price_per_quintal_inr: float = Field(ge=0.0)
    expected_price_per_quintal_inr: float | None = Field(
        default=None,
        ge=0.0,
    )

    trend: MarketTrend

    confidence: float = Field(ge=0.0, le=1.0)

    summary: str = Field(min_length=1)
    factors: list[str] = Field(default_factory=list)

    disclaimer: str | None = None


__all__ = [
    "MarketInsight",
    "MarketPrice",
    "MarketPriceSource",
    "MarketTrend",
]