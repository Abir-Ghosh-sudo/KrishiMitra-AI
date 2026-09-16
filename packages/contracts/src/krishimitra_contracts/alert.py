"""Alert service contracts for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AlertSeverity(StrEnum):
    """Severity levels for farmer-facing alerts."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(StrEnum):
    """Types of agricultural alerts."""

    WEATHER = "weather"
    DISEASE = "disease"
    PEST = "pest"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    CROP = "crop"
    MARKET = "market"
    SUSTAINABILITY = "sustainability"
    SYSTEM = "system"


class AlertContract(BaseModel):
    """Contract for an alert exchanged between KrishiMitra services."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    alert_id: UUID

    farmer_id: UUID
    farm_id: UUID | None = None

    alert_type: AlertType
    severity: AlertSeverity

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    created_at: datetime

    expires_at: datetime | None = None

    requires_action: bool = False

    action_text: str | None = Field(
        default=None,
        max_length=500,
    )

    source: str = Field(
        min_length=1,
        max_length=100,
    )


__all__ = [
    "AlertContract",
    "AlertSeverity",
    "AlertType",
]