"""Authorization primitives for KrishiMitra-AI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from krishimitra_security.permissions import Permission
from krishimitra_security.roles import Role


class AuthorizationError(PermissionError):
    """Raised when a principal is not authorized for an action."""


class AuthorizationDecision(StrEnum):
    """Result of an authorization check."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """Context used when evaluating an authorization request."""

    principal_id: UUID
    roles: frozenset[Role] = frozenset()
    permissions: frozenset[Permission] = frozenset()


@dataclass(frozen=True, slots=True)
class AuthorizationResult:
    """Detailed result of an authorization check."""

    decision: AuthorizationDecision
    permission: Permission
    reason: str | None = None

    @property
    def allowed(self) -> bool:
        """Return whether the action is authorized."""

        return self.decision is AuthorizationDecision.ALLOW


class AuthorizationService:
    """Evaluate role and permission based access decisions."""

    def __init__(
        self,
        *,
        role_permissions: dict[Role, frozenset[Permission]] | None = None,
    ) -> None:
        self._role_permissions = role_permissions or {}

    def resolve_permissions(
        self,
        roles: frozenset[Role],
    ) -> frozenset[Permission]:
        """Resolve all permissions granted by a set of roles."""

        permissions: set[Permission] = set()

        for role in roles:
            permissions.update(
                self._role_permissions.get(
                    role,
                    frozenset(),
                ),
            )

        return frozenset(permissions)

    def authorize(
        self,
        context: AuthorizationContext,
        permission: Permission,
    ) -> AuthorizationResult:
        """Check whether the principal has the requested permission."""

        role_permissions = self.resolve_permissions(context.roles)
        effective_permissions = context.permissions | role_permissions

        if permission in effective_permissions:
            return AuthorizationResult(
                decision=AuthorizationDecision.ALLOW,
                permission=permission,
            )

        return AuthorizationResult(
            decision=AuthorizationDecision.DENY,
            permission=permission,
            reason="permission_not_granted",
        )

    def require(
        self,
        context: AuthorizationContext,
        permission: Permission,
    ) -> None:
        """Require a permission or raise AuthorizationError."""

        result = self.authorize(
            context,
            permission,
        )

        if not result.allowed:
            raise AuthorizationError(
                result.reason or "authorization_failed",
            )


__all__ = [
    "AuthorizationContext",
    "AuthorizationDecision",
    "AuthorizationError",
    "AuthorizationResult",
    "AuthorizationService",
]