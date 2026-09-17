"""Permission definitions for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    """Fine-grained permissions used by KrishiMitra services."""

    # Farmer and farm management
    FARMER_READ = "farmer:read"
    FARMER_WRITE = "farmer:write"

    FARM_READ = "farm:read"
    FARM_WRITE = "farm:write"

    # Agricultural intelligence
    CROP_READ = "crop:read"
    CROP_WRITE = "crop:write"

    DIAGNOSIS_READ = "diagnosis:read"
    DIAGNOSIS_CREATE = "diagnosis:create"

    PREDICTION_READ = "prediction:read"
    PREDICTION_CREATE = "prediction:create"

    RECOMMENDATION_READ = "recommendation:read"
    RECOMMENDATION_CREATE = "recommendation:create"

    SIMULATION_READ = "simulation:read"
    SIMULATION_CREATE = "simulation:create"

    # Documents and knowledge
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPLOAD = "document:upload"

    RAG_READ = "rag:read"
    RAG_MANAGE = "rag:manage"

    # Alerts and feedback
    ALERT_READ = "alert:read"
    ALERT_CREATE = "alert:create"

    FEEDBACK_READ = "feedback:read"
    FEEDBACK_CREATE = "feedback:create"

    # Expert workflows
    EXPERT_CASE_READ = "expert_case:read"
    EXPERT_CASE_REVIEW = "expert_case:review"

    # Market and sustainability
    MARKET_READ = "market:read"
    SUSTAINABILITY_READ = "sustainability:read"

    # Administration
    USER_READ = "user:read"
    USER_MANAGE = "user:manage"

    AUDIT_READ = "audit:read"

    SYSTEM_READ = "system:read"
    SYSTEM_MANAGE = "system:manage"


def permission_value(permission: Permission) -> str:
    """Return the stable string representation of a permission."""

    return permission.value


def is_valid_permission(value: str) -> bool:
    """Return whether a string represents a known permission."""

    try:
        Permission(value)
    except ValueError:
        return False

    return True


__all__ = [
    "Permission",
    "is_valid_permission",
    "permission_value",
]