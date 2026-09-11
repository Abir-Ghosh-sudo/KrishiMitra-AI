"""Agricultural alert models for KrishiMitra-AI."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AlertSeverity(StrEnum):
    """Severity levels for agricultural alerts."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertCategory(StrEnum):
    """Agricultural alert categories."""

    WEATHER = "weather"
    IRRIGATION = "irrigation"
    DISEASE = "disease"
    PEST = "pest"
    CROP = "crop"
    SOIL = "soil"
    MARKET = "market"
    SUSTAINABILITY = "sustainability"
    SYSTEM = "system"


class Alert(BaseModel):
    """Actionable alert delivered to a farmer."""

    model_config = ConfigDict(extra="forbid")

    alert_id: UUID
    farmer_id: UUID
    farm_id: UUID | None = None

    category: AlertCategory
    severity: AlertSeverity

    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1)

    action_required: bool = False
    recommended_action: str | None = None

    created_at: datetime
    expires_at: datetime | None = None

    acknowledged: bool = False
    acknowledged_at: datetime | None = None


__all__ = [
    "Alert",
    "AlertCategory",
    "AlertSeverity",
]