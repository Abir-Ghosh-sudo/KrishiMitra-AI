"""Role definitions and permission mappings for KrishiMitra-AI."""

from __future__ import annotations

from enum import StrEnum

from krishimitra_security.permissions import Permission


class Role(StrEnum):
    """Application roles used for role-based access control."""

    FARMER = "farmer"
    EXPERT = "expert"
    ADMIN = "admin"
    SERVICE = "service"
    SYSTEM = "system"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.FARMER: frozenset(
        {
            Permission.FARMER_READ,
            Permission.FARMER_WRITE,
            Permission.FARM_READ,
            Permission.FARM_WRITE,
            Permission.CROP_READ,
            Permission.DIAGNOSIS_READ,
            Permission.DIAGNOSIS_CREATE,
            Permission.PREDICTION_READ,
            Permission.PREDICTION_CREATE,
            Permission.RECOMMENDATION_READ,
            Permission.RECOMMENDATION_CREATE,
            Permission.SIMULATION_READ,
            Permission.SIMULATION_CREATE,
            Permission.DOCUMENT_READ,
            Permission.DOCUMENT_UPLOAD,
            Permission.ALERT_READ,
            Permission.FEEDBACK_CREATE,
            Permission.MARKET_READ,
            Permission.SUSTAINABILITY_READ,
        }
    ),
    Role.EXPERT: frozenset(
        {
            Permission.FARMER_READ,
            Permission.FARM_READ,
            Permission.CROP_READ,
            Permission.DIAGNOSIS_READ,
            Permission.DIAGNOSIS_CREATE,
            Permission.PREDICTION_READ,
            Permission.RECOMMENDATION_READ,
            Permission.RECOMMENDATION_CREATE,
            Permission.DOCUMENT_READ,
            Permission.ALERT_READ,
            Permission.FEEDBACK_READ,
            Permission.EXPERT_CASE_READ,
            Permission.EXPERT_CASE_REVIEW,
            Permission.MARKET_READ,
            Permission.SUSTAINABILITY_READ,
        }
    ),
    Role.ADMIN: frozenset(
        {
            Permission.FARMER_READ,
            Permission.FARMER_WRITE,
            Permission.FARM_READ,
            Permission.FARM_WRITE,
            Permission.CROP_READ,
            Permission.CROP_WRITE,
            Permission.DIAGNOSIS_READ,
            Permission.DIAGNOSIS_CREATE,
            Permission.PREDICTION_READ,
            Permission.PREDICTION_CREATE,
            Permission.RECOMMENDATION_READ,
            Permission.RECOMMENDATION_CREATE,
            Permission.SIMULATION_READ,
            Permission.SIMULATION_CREATE,
            Permission.DOCUMENT_READ,
            Permission.DOCUMENT_UPLOAD,
            Permission.RAG_READ,
            Permission.RAG_MANAGE,
            Permission.ALERT_READ,
            Permission.ALERT_CREATE,
            Permission.FEEDBACK_READ,
            Permission.FEEDBACK_CREATE,
            Permission.EXPERT_CASE_READ,
            Permission.EXPERT_CASE_REVIEW,
            Permission.MARKET_READ,
            Permission.SUSTAINABILITY_READ,
            Permission.USER_READ,
            Permission.USER_MANAGE,
            Permission.AUDIT_READ,
            Permission.SYSTEM_READ,
        }
    ),
    Role.SERVICE: frozenset(
        {
            Permission.FARM_READ,
            Permission.CROP_READ,
            Permission.DIAGNOSIS_READ,
            Permission.DIAGNOSIS_CREATE,
            Permission.PREDICTION_READ,
            Permission.PREDICTION_CREATE,
            Permission.RECOMMENDATION_READ,
            Permission.RECOMMENDATION_CREATE,
            Permission.DOCUMENT_READ,
            Permission.RAG_READ,
            Permission.ALERT_READ,
            Permission.ALERT_CREATE,
            Permission.FEEDBACK_READ,
            Permission.EXPERT_CASE_READ,
            Permission.MARKET_READ,
            Permission.SUSTAINABILITY_READ,
            Permission.SYSTEM_READ,
        }
    ),
    Role.SYSTEM: frozenset(Permission),
}


def permissions_for_role(role: Role) -> frozenset[Permission]:
    """Return the permissions granted to a role."""

    return ROLE_PERMISSIONS.get(role, frozenset())


def has_permission(
    role: Role,
    permission: Permission,
) -> bool:
    """Return whether a role grants a specific permission."""

    return permission in permissions_for_role(role)


def roles_for_permission(
    permission: Permission,
) -> frozenset[Role]:
    """Return all roles that grant a specific permission."""

    return frozenset(
        role
        for role, permissions in ROLE_PERMISSIONS.items()
        if permission in permissions
    )


__all__ = [
    "ROLE_PERMISSIONS",
    "Role",
    "has_permission",
    "permissions_for_role",
    "roles_for_permission",
]